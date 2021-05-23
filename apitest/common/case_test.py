# coding:utf-8
import os
import time
import requests
import pytest
from json import JSONDecodeError
from apitest.common.header_mange import HeaderManage

from apitest.common.emailer import Email
from apitest.common.reporter import Template_mixin


class TestCaseRequest:
    def __init__(self, case_list, host):
        self.case_list = case_list
        self.host = host
        self.header = HeaderManage.read_header(2)
        self.table_tr_fail = self.table_tr_success = ''
        self.num_success = self.num_fail = 0
        self.html = Template_mixin()

    def flow_api_test(self, data_list):
        count = len(data_list)  # 每个必须都成功
        self.single_api_test()
        if self.num_success == count:
            return True
        else:
            return False

    def single_api_test(self):
        for case in self.case_list:
            result = request(case, self.host, self.header)
            if result.status_code == 401:
                HeaderManage.update_header(2, self.host)
                self.header = HeaderManage.read_header(2)
                result = request(case, self.host, self.header)
            self.save_report_info(result, case)

            # 测试结果存数据库
            api_response = "这里我有解决不了的问题，先放着"
            case.append(result.status_code)
            case.append(api_response)
            case.append(result.status_code == case[5])
        report_file(self.num_fail, self.num_success, self.html, self.table_tr_fail, self.table_tr_success)
        return self.case_list

    def save_report_info(self, result, case):
        if result.status_code != case[5]:
            self.num_fail += 1
            try:
                result_json = result.json()
            except JSONDecodeError:
                result_json = '由于异常，无法读取结果'
            btw = '可能的原因：\n' \
                  '1、某个参数没加required等于true\n' \
                  '2、参数类型传错了（请联系QA）\n' \
                  '3、真bug'
            table_td = self.html.TABLE_TMPL_FAIL % dict(runtime=time.strftime('%Y-%m-%d %H:%M:%S'), interface=case[1],
                                                        method=case[2], parameters=case[3], body=case[4], expectcode=case[5],
                                                        testresult='测试失败', testcode=result.status_code, resultbody=result_json,
                                                        btw=btw)
            self.table_tr_fail += table_td
        else:
            self.num_success += 1
            table_td = self.html.TABLE_TMPL_SUCC % dict(runtime=time.strftime('%Y-%m-%d %H:%M:%S'), interface=case[1],
                                                        method=case[2], parameters=case[3], body=case[4], expectcode=case[5],
                                                        testresult='测试成功', testcode=result.status_code,)
            self.table_tr_success += table_td


def report_file(num_fail, num_success, html, table_tr_fail, table_tr_success):
    total_str = '共 %s，通过 %s，失败 %s' % (num_fail + num_success, num_success, num_fail)
    output = html.HTML_TMPL % dict(value=total_str, table_tr=table_tr_fail, table_tr2=table_tr_success, )

    # 生成html报告
    filename = '{date}_TestReport.html'.format(date=time.strftime('%Y%m%d%H'))
    root = os.path.abspath('.')
    filepath = os.path.join(root, 'apitest/report/'+filename)

    with open(filepath, 'wb') as f:
        f.write(output.encode('utf8'))

    if num_fail > 0:
        Email(num_fail).send_email()
    return


def request(case, host, header):
    if case[2] == 'get' or case[2] == 'GET':
        result = requests.get(host + case[1], headers=header, params=case[3], json=case[4])
    else:
        result = requests.post(host + case[1], json=case[4], headers=header)
    return result


# class TestApi:
#     def test1(self):
#         print('ok you mf')
#
#
# def test_answer(cmdopt):
#     print(cmdopt)
#     # if cmdopt == 'type1':
#     #     print('first')
#     # elif cmdopt == 'type2':
#     #     print('second')
#     assert 1


