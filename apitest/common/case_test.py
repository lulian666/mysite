# coding:utf-8
import inspect
import os
import time

import jsonpath
import requests
import pytest
from json import JSONDecodeError
from apitest.common.header_mange import HeaderManage

from apitest.common.emailer import Email
from apitest.common.reporter import Template_mixin


class TestCaseRequest:
    def __init__(self):
        self.header = HeaderManage.read_header(2)
        self.table_tr_fail = self.table_tr_success = ''
        self.num_success = self.num_fail = 0
        self.html = Template_mixin()

    def flow_api_case_test(self, multiple_case_list):
        # multiple_case_list实际上就是包含多个case_list的list
        # 每个item里第一项是case_list，第二项是他的io_list，第三项是host
        count = len(multiple_case_list)
        success_number = 0
        for item in multiple_case_list:
            # print("让我瞅瞅每个item长啥样来着：", item)
            item_success = self.flow_api_single_case_test(item[1], item[0], item[2])
            if item_success:
                success_number = success_number + 1
            # print("case测试通过了吗？", item_success)
        report_file(self.num_fail, self.num_success, self.html, self.table_tr_fail, self.table_tr_success)
        if count == success_number:
            print("所有case都通过了！")
            return True
        else:
            print("有case没通过")
            return False

    def flow_api_single_case_test(self, io_list, case_list, host):
        num_success = 0
        # print("让我瞅瞅case_list长啥样来着：", case_list)
        # print("让我瞅瞅io_list长啥样来着：", io_list)
        count = len(case_list)  # 每个必须都成功
        # print("case_list中有几个case：", len(case_list))
        parameters = []  # [[id, 出参名称, 值],]
        for index, case in enumerate(case_list):
            if io_list[index][1] != '':  # 如果有入参，入参应该只允许选择已有的出参
                case = input_parameter(io_list[index][1], case, parameters)

            # 去测试
            result = test_avoid_401(case, host, self.header)

            called_by = inspect.currentframe().f_back.f_code.co_name
            # print("我的调用方是：", called_by)
            if called_by == "flow_api_case_test":
                print("正在保存测试结果。。。")
                self.save_report_info(result, case)

            if result.status_code == case[5]:
                num_success = num_success + 1
            # 保存出参
            if io_list[index][0] != '':
                value = output_parameter(io_list[index][0], result)  # 这里应该保存
                parameters.append([case[0], "name_placeholder", value])

        return num_success == count

    def single_api_test(self, case_list, host):
        for case in case_list:
            result = test_avoid_401(case, host, self.header)
            self.save_report_info(result, case)

            # 测试结果存数据库
            api_response = "这里我有解决不了的问题，先放着"
            case.append(result.status_code)
            case.append(api_response)
            case.append(result.status_code == case[5])
        report_file(self.num_fail, self.num_success, self.html, self.table_tr_fail, self.table_tr_success)
        return case_list

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


def output_parameter(json_pattern, result):
    json_data = result.json()
    value = jsonpath.jsonpath(json_data, json_pattern)
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


def test_avoid_401(case, host, header):
    result = request(case, host, header)
    if result.status_code == 401:
        HeaderManage.update_header(2, host)
        header = HeaderManage.read_header(2)
        result = request(case, host, header)
    return result
