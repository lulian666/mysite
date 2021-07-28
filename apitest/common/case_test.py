# coding:utf-8
import inspect
import json
import os
import time

import jsonpath
import requests
import pytest
from json import JSONDecodeError
from apitest.common.header_mange import HeaderManage

from apitest.common.emailer import Email
from apitest.common.reporter import TemplateMixin
from apitest.models import Apis


class TestCaseRequest:
    def __init__(self, tester, product_id):
        self.header = HeaderManage.read_header(product_id)
        self.table_tr_fail = self.table_tr_success = ''
        self.num_success = self.num_fail = 0
        self.html = TemplateMixin()
        self.tester = tester

    def flow_api_case_test(self, multiple_case_list):
        # multiple_case_list实际上就是包含多个case_list的list
        # 每个item里第一项是case_list，第二项是他的io_list，第三项是host
        count = len(multiple_case_list)
        success_number = 0
        for item in multiple_case_list:
            item_success, try_refresh_token = self.flow_api_single_case_test(item[1], item[0], item[2])
            if item_success:
                success_number = success_number + 1
        report_file(self.num_fail, self.num_success, self.html, self.table_tr_fail, self.table_tr_success, "流程接口测试", self.tester)
        if count == success_number:
            return True, try_refresh_token
        else:
            return False, try_refresh_token

    def flow_api_single_case_test(self, io_list, case_list, host):
        num_success = 0
        count = len(case_list)  # 每个必须都成功
        parameters = []  # [[id, 出参名称, 值],]
        for index, case in enumerate(case_list):
            if io_list[index][1] != '':  # 如果有入参，入参应该只允许选择已有的出参
                case = input_parameter(io_list[index][1], case, parameters)

            # 去测试
            result, try_refresh_token = self.test_avoid_401(case, host)
            if try_refresh_token:
                print('----------')
                print('测试api：', case[1])
                print('测试结果：')
                print(result.status_code)
                print(result.json())

                called_by = inspect.currentframe().f_back.f_code.co_name
                if called_by == "flow_api_case_test":
                    self.save_report_info(result, case)

                if result.status_code == case[5]:
                    num_success = num_success + 1
                # 保存出参
                if io_list[index][0] != '':
                    value = output_parameter(io_list[index][0], result)  # 这里应该保存
                    parameters.append([case[0], "name_placeholder", value])
            else:
                num_success = 0
        return num_success == count, try_refresh_token

    def single_api_test(self, case_list, host):
        try_refresh_token = True
        for case in case_list:
            print('----------')
            print('case:', case)
            result, try_refresh_token = self.test_avoid_401(case, host)
            if try_refresh_token:
                # print('测试api：', case[1])
                if int(result.status_code) != int(case[5]):
                    print('测试失败')
                    print('预期状态码：', case[5])
                    print("result.status_code:", result.status_code)
                    try:
                        result_json = result.json()
                    except JSONDecodeError:
                        result_json = result.content
                    print("result_json:", result_json)
                    # print("case[5]:", case[5])
                self.save_report_info(result, case)
                # 测试结果存数据库
                api_response = "这里我有解决不了的问题，先放着"
                case.append(result.status_code)
                case.append(api_response)
                case.append(result.status_code == case[5])
            else:
                report_file(0, 0, self.html, self.table_tr_fail, self.table_tr_success, "单接口测试", self.tester)
                break
        report_file(self.num_fail, self.num_success, self.html, self.table_tr_fail, self.table_tr_success, "单接口测试", self.tester)
        return result, case_list, try_refresh_token

    def save_report_info(self, result, case):
        if result.status_code != case[5]:
            self.num_fail += 1
            try:
                result_json = result.json()
            except JSONDecodeError:
                result_json = result.content
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

    def test_avoid_401(self, case, host):
        try_refresh_token = True
        result = request(case, host, self.header)

        if result.status_code == 401:
            print('token 过期，正在刷新。。。')
            case_id = case[0]
            product_id = Apis.objects.get(id=case_id).Product_id
            try_refresh_token = HeaderManage.update_header(product_id, host)
            self.header = HeaderManage.read_header(product_id)
            result = request(case, host, self.header)
            print('刷新token过后，状态码：', result.status_code)
        return result, try_refresh_token


def report_file(num_fail, num_success, html, table_tr_fail, table_tr_success, called_by, tester):
    if num_success > 0:
        total_str = '共 %s，通过 %s，失败 %s' % (num_fail + num_success, num_success, num_fail)
        output = html.HTML_TMPL % dict(value=total_str, table_tr=table_tr_fail, table_tr2=table_tr_success, )
        is_success = "PASS" if num_success == (num_fail + num_success) else "FAIL"

        # 生成html报告
        filename = '{called_by}_{date}_{is_success}_{tester}_TestReport.html'.format(date=time.strftime('%Y.%m.%d-%H:%M'), called_by=called_by, is_success=is_success, tester=tester)
        root = os.path.abspath('.')
        filepath = os.path.join(root, 'apitest/templates/report/' + filename)

        with open(filepath, 'wb') as f:
            f.write(output.encode('utf8'))

        if num_fail > 0:
            Email(num_fail).send_email()
    return


def request(case, host, header):
    url = host + case[1]
    json_data = json.dumps(case[4]) if len(case[4]) > 0 else {}
    if case[2].lower() == 'get':
        result = requests.get(url=url, headers=header, params=case[3], data=json_data)
    else:
        result = requests.post(url=url, data=json_data, headers=header)
    return result


def output_parameter(json_pattern, result):
    try:
        json_data = result.json()
        value = jsonpath.jsonpath(json_data, json_pattern)
    except JSONDecodeError:
        value = '由于异常，无法读取结果'
    return value


def input_parameter(parameter, case, parameters):
    name = parameter.split('=')[0]
    api_id = int(parameter.split('=')[1])

    if case[2] == 'get' or case[2] == 'GET':
        case[3] = replace(name, case[3], api_id, parameters)
    else:
        case[4] = replace(name, case[4], api_id, parameters)
    return case


def replace(name, json_string, api_id, parameters):
    for item in parameters:
        if api_id == item[0]:
            value = item[2]
            break
    for key, key_value in json_string.items():
        if name == key:
            try:
                json_string[key] = value
            except:
                pass
    return json_string



