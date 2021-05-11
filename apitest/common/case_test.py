# coding:utf-8

import os
import sys
import time
import requests
from json import JSONDecodeError
from apitest.common.header_mange import HeaderManage

from apitest.common.emailer import Email
from apitest.common.reporter import Template_mixin

direct = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(direct)
sys.path.append('/usr/lib/python2.7/site-packages (2.22.0)')


class CaseRequest:
    def __init__(self):
        self.table_tr_fail = ''
        self.table_tr_success = ''

        self.num_success = 0
        self.num_fail = 0
        self.html = Template_mixin()

    def send_request(self, case_list, host):
        # header 改从数据库里获取
        header = HeaderManage().readHeader(2)
        for case in case_list:
            if case[2] == 'get' or case[2] == 'GET':
                result = requests.get(host + case[1], headers=header, params=case[3], json=case[4])
            elif case[2] == 'post' or case[2] == 'POST':
                result = requests.post(host + case[1], json=case[4], headers=header)
            if result.status_code == 401:
                print('401了')
                HeaderManage().updateHeader(2,host)
                header = HeaderManage().readHeader(2)
                if case[2] == 'get' or case[2] == 'GET':
                    result = requests.get(host + case[1], headers=header, params=case[3], json=case[4])
                else:
                    result = requests.post(host + case[1], json=case[4], headers=header)

            # 下面是存报告信息的
            if result.status_code != case[5]:
                apistatus = False
                print('测试失败')
                self.num_fail +=1
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
                                                            method=case[2], parameters=case[3], body=case[4], expectcode=case[5],
                                                            testresult='测试失败', testcode=result.status_code,resultbody=result_json,
                                                            btw=btw)
                self.table_tr_fail += table_td
            else:
                apistatus = True
                print('测试成功')
                self.num_success +=1
                table_td = self.html.TABLE_TMPL_SUCC % dict(runtime=time.strftime('%Y-%m-%d %H:%M:%S'), interface=case[1],
                                                            method=case[2], parameters=case[3], body=case[4], expectcode=case[5],
                                                            testresult='测试成功', testcode=result.status_code,)
                self.table_tr_success += table_td
            print('---------')
            # 存数据库信息
            apiresponsestatuscode = result.status_code
            apiresponse = "这里我有解决不了的问题，先放着"
            case.append(apiresponsestatuscode)
            case.append(apiresponse)
            case.append(apistatus)
        self.report()
        return case_list

    def report(self):
        total_str = '共 %s，通过 %s，失败 %s' % (self.num_fail + self.num_success, self.num_success, self.num_fail)
        output = self.html.HTML_TMPL % dict(value=total_str, table_tr=self.table_tr_fail, table_tr2=self.table_tr_success, )

        # 生成html报告
        filename = '{date}_TestReport.html'.format(date=time.strftime('%Y%m%d%H'))

        # 获取report的路径
        root = os.path.abspath('.') #获取当前工作目录路径
        filepath = os.path.join(root, 'apitest/report/'+filename)

        with open(filepath, 'wb') as f:
            f.write(output.encode('utf8'))

        if self.num_fail > 0:
            Email(self.num_fail).send_email()
        return

    def get_num_fail(self):
        return self.num_fail
