# coding:utf-8

import os
import sys
import time
from json import JSONDecodeError

from apitest.common.manage_sql import *

dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir)
sys.path.append('/usr/lib/python2.7/site-packages (2.22.0)')

import requests
import json

from emailer import Email
from read_config import Read_config
from refresh_token import Refresh_token
from reporter import Template_mixin

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
        with open('../config/header_kuainiao.json', 'r', encoding='utf8')as fp:
            header = json.load(fp)
            print('header：', header)
        fp.close()
        for case in case_list:
            if case[2] == 'get' or case[2] == 'GET':
                result = requests.get(host + case[1], headers=header, params=case[3], json=case[4])
            elif case[2] == 'post' or case[2] == 'POST':
                result = requests.post(host + case[1], json=case[4], headers=header)
                # print(type(case[4]))
                # print('url:', host + case[1])
                # print('case[4]:', case[4])
            if result.status_code == 401:
                print('401了')
                Refresh_token().refresh()
                with open('../config/header_kuainiao.json', 'r', encoding='utf8')as fp:
                    header = json.load(fp)
                if case[2] == 'get' or case[2] == 'GET':
                    result = requests.get(host + case[1], headers=header, params=case[3], json=case[4])
                else:
                    result = requests.post(host + case[1], json=case[4], headers=header)


            # 下面是存报告信息的
            if result.status_code != case[5]:
                apistatus = False
                print('测试失败')
                self.numfail +=1
                print('case:', case)
                print('预期状态码',case[5])
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
                table_td = self.html.TABLE_TMPL_FAIL % dict(runtime=time.strftime('%Y-%m-%d %H:%M:%S'), interface=case[1],
                                                            method=case[1], parameters=case[3], body=case[4], expectcode=case[5],
                                                            testresult='测试失败', testcode=result.status_code,resultbody=result_json,
                                                            btw=btw)
                self.table_tr_fail += table_td
            else:
                apistatus = True
                print('测试成功')
                self.numsucc +=1
                table_td = self.html.TABLE_TMPL_SUCC % dict(runtime=time.strftime('%Y-%m-%d %H:%M:%S'), interface=case[1],
                                                            method=case[2], parameters=case[3], body=case[4], expectcode=case[5],
                                                            testresult='测试成功', testcode=result.status_code,)
                self.table_tr_succ += table_td
            print('---------')
            # 存数据库信息
            apiresponsestatuscode = result.status_code
            # try:
            #     apiresponse = result.json()
            # except JSONDecodeError:
            #     apiresponse = '由于异常，无法读取结果'
            apiresponse = "这里我有解决不了的问题，先放着"
            case.append(apiresponsestatuscode)
            case.append(apiresponse)
            case.append(apistatus)
            Manage_sql().updateCaseToSQL([case,])
        self.report()
        return case_list

    def report(self):

        total_str = '共 %s，通过 %s，失败 %s' % (self.numfail + self.numsucc, self.numsucc, self.numfail)
        output = self.html.HTML_TMPL % dict(value=total_str, table_tr=self.table_tr_fail, table_tr2=self.table_tr_succ, )

        # 生成html报告
        filename = '{date}_TestReport.html'.format(date=time.strftime('%Y%m%d%H'))

        # 获取report的路径
        # dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../report')
        # filename = os.path.join(dir, filename)
        filename

        with open('../report/'+filename, 'wb') as f:
            f.write(output.encode('utf8'))

        if self.numfail > 0:
            Email(self.numfail).send_email()
        return

    def get_numfail(self):
        return self.numfail

if __name__ == '__main__':

    print('Fine!')