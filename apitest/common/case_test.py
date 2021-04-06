# coding:utf-8

import os
import sys
import time
from json import JSONDecodeError

dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir)
sys.path.append('/usr/lib/python2.7/site-packages (2.22.0)')

import requests
import json

from config import Email
from config import Read_config
from common.refresh_token import Refresh_token
from common.reporter import Template_mixin

'''
requests.post()用data参数提交数据时，request.body的内容则为a=1&b=2的这种形式，用json参数提交数据时，request.body的内容则为'{"a": 1, "b": 2}'的这种形式
'''



class Case_request:
    def __init__(self):
        self.table_tr_fail = ''
        self.table_tr_succ = ''

        self.numsucc = 0
        self.numfail = 0
        self.html = Template_mixin()


    def send_request(self, case_list):
        host = Read_config().get_value('REQUEST', 'host')
        #还需要header
        with open('./header_kuainiao.json', 'r', encoding='utf8')as fp:
            header = json.load(fp)
        fp.close()
        for case in case_list:
            if case[1] == 'get' or case[1] == 'GET':
                result = requests.get(host + case[0], headers=header, params=case[2], json=case[3])
            elif case[1] == 'post' or case[1] == 'POST':
                result = requests.post(host + case[0], json=case[3], headers=header)
            if result.status_code == 401:
                print('401了')
                Refresh_token().refresh()
                with open('./header_kuainiao.json', 'r', encoding='utf8')as fp:
                    header = json.load(fp)
                if case[1] == 'get':
                    result = requests.get(host + case[0], headers=header, params=case[2], json=case[3])
                else:
                    result = requests.post(host + case[0], json=case[3], headers=header)
            if result.status_code != case[4]:
                print('测试失败')
                self.numfail +=1
                print('case:', case)
                print('预期状态码',case[4])
                print('实际状态码',result.status_code)
                result_json = ''
                try:
                    result_json = result.json()
                except JSONDecodeError:
                    result_json = '由于异常，无法读取结果'
                print('请求结果',result_json)
                print()
                btw = '可能的原因：\n' \
                      '1、某个参数没加required等于true\n' \
                      '2、参数类型传错了（请联系QA）\n' \
                      '3、真bug'
                table_td = self.html.TABLE_TMPL_FAIL % dict(runtime=time.strftime('%Y-%m-%d %H:%M:%S'), interface=case[0],
                                                            method=case[1], parameters=case[2], body=case[3], expectcode=case[4],
                                                            testresult='测试失败', testcode=result.status_code,resultbody=result_json,
                                                            btw=btw)
                self.table_tr_fail += table_td
            else:
                print('测试成功')
                self.numsucc +=1
                table_td = self.html.TABLE_TMPL_SUCC % dict(runtime=time.strftime('%Y-%m-%d %H:%M:%S'), interface=case[0],
                                                            method=case[1], parameters=case[2], body=case[3], expectcode=case[4],
                                                            testresult='测试成功', testcode=result.status_code,)
                self.table_tr_succ += table_td
            print('---------')
        self.report()


        return

    def report(self):

        total_str = '共 %s，通过 %s，失败 %s' % (self.numfail + self.numsucc, self.numsucc, self.numfail)
        output = self.html.HTML_TMPL % dict(value=total_str, table_tr=self.table_tr_fail, table_tr2=self.table_tr_succ, )

        # 生成html报告
        filename = '{date}_TestReport.html'.format(date=time.strftime('%Y%m%d%H'))

        # 获取report的路径
        dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'report')
        filename = os.path.join(dir, filename)

        with open(filename, 'wb') as f:
            f.write(output.encode('utf8'))

        if self.numfail > 0:
            Email(self.numfail).send_email()
        return

    def get_numfail(self):
        return self.numfail