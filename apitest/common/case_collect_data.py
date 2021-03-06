# coding:utf-8
import os
from fnmatch import fnmatch
import json

import jsonpath

from apitest.common.case_generate_cases import CaseGenerate


class CaseCollect:
    # 排除一些不需要测试的接口（在前端输入），比如内部接口，比如需要具体id的，但是id会过期的（商品id，卡片id），以及一些无法测试的比如绑定微信等
    # 这里包括了橙和快鸟的
    root = os.path.abspath('.')  # 获取当前工作目录路径
    filepath = os.path.join(root, 'apitest/config/temp.json')

    def collect_data_accordingly(self, interfaces_not_wanted, product_id):
        basic_case_list, case_list = [], []
        # 处理interfaces_not_wanted，传进来的是string
        if interfaces_not_wanted:
            interfaces_not_wanted = interfaces_not_wanted.split(',')
        with open(self.filepath, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
        if product_id in ["1", "3"]:  # 1和3分别代表橙和即刻夸夸项目
            print("按即刻接口文档格式解析")
            basic_case_list, case_list = self.collect_data_jike(json_data, interfaces_not_wanted)
        elif product_id in ["4"]:
            print("按小宇宙接口文档格式解析")
            basic_case_list, case_list = self.collect_data_podcast(json_data, interfaces_not_wanted)
        else:
            path_data = json_data['paths']
            print("按即刻接口swagger文档格式解析")
            basic_case_list, case_list = self.collect_data_swagger(json_data, path_data, interfaces_not_wanted)

        return basic_case_list, case_list

    @staticmethod
    def collect_data_podcast(json_data, interfaces_not_wanted):
        basic_case_list, case_list = [], []
        # 小宇宙的文档结构，是同一个功能的都放在一个结构里，json_data 里的每个都可能包含不止一个 api
        # for apis in json_data:
        #     if 'item' in apis:
        #         for api in apis['item']:
        #             parameters, body = {}, {}
        #             url, method, case_name = '', '', ''
        #             if 'url' in str(api):
        #                 url = jsonpath.jsonpath(api, "$.url")[0]
        # 小宇宙json文档待优化，先不解析
        return basic_case_list, case_list

    # 这里会删除所有老的case，把新的case写进数据库里面
    @staticmethod
    def collect_data_swagger(json_data, path_data, interfaces_not_wanted):
        basic_case_list, case_list = [], []
        # 如果不照着json文件看，可能会理解上有困难
        for path_keys in path_data:
            url = path_keys
            method = list(path_data[url].keys())[0]
            case_wanted = True
            if interfaces_not_wanted:
                for each in interfaces_not_wanted:
                    if fnmatch(url, "*" + each + "*"):
                        case_wanted = False

            # 有一些废弃的接口，也要排除一下
            if 'deprecated' in path_data[url].get(method):
                deprecated = path_data[url].get(method).get('deprecated')
                if deprecated is True:
                    case_wanted = False
            # 很烦人的是有时候method大小写还不一致，有时候是post，有时候是POST……也要处理一下
            if case_wanted:
                for path_values in path_data[url]:
                    other_info = path_data[url][method]
                    if 'summary' in other_info:
                        case_name = other_info['summary']
                    if 'parameters' in other_info:  # 如果有parameters的话，有的接口是没有的
                        parameters_maybe = other_info['parameters']
                        parameters = {}
                        body = {}
                        father = ''
                        son_json = {}
                        for params in parameters_maybe:
                            if params['in'] == 'query' or params['in'] == 'path':  # 代表是parameters
                                parameters, son_json, father = parameters_info_swagger(params, parameters, son_json,
                                                                                       father)
                            else:  # 如果是body的话
                                body, son_json, father = body_info_swagger(params, json_data, body, son_json, father)
                        # 这俩遍历是用来寻找参数中2级json的父级
                        for item in parameters:
                            if item == father:
                                parameters[item].update({"son": son_json})
                        for item in body:
                            if item == father:
                                body[item].update({"son": son_json})
                    else:
                        parameters = {}
                        body = {}

                basic_case_list.append([case_name, url, method, parameters, body])
                case_list = CaseGenerate(case_name, url, method, parameters, body).generate()
        return basic_case_list, case_list

    @staticmethod
    def collect_data_jike(json_data, interfaces_not_wanted):
        basic_case_list, case_list = [], []
        for api in json_data:
            parameters, body = {}, {}
            url, method, case_name = '', '', ''
            if 'url' in api:
                url = jsonpath.jsonpath(api, "$.url")[0]
            case_wanted = True
            if interfaces_not_wanted:
                for each in interfaces_not_wanted:
                    if fnmatch(url, "*" + each + "*"):
                        case_wanted = False
            if case_wanted:
                if 'type' in api:
                    method = jsonpath.jsonpath(api, "$.type")[0]
                if 'title' in api:
                    case_name = jsonpath.jsonpath(api, "$.title")[0]
                if "parameter" in api:
                    parameters_data = jsonpath.jsonpath(api, "$.parameter")
                else:
                    parameters_data = {}
                if parameters_data != {}:
                    if method.lower() == "post":
                        body = parameters_info_jike(parameters_data)
                        # print('body:', body, type(body))
                    else:
                        parameters = parameters_info_jike(parameters_data)
                        # print('parameters:', parameters, type(parameters))
                else:
                    parameters = {}
                    body = {}
                if url != '':
                    basic_case_list.append([case_name, url, method, parameters, body])
                    case_list = CaseGenerate(case_name, url, method, parameters, body).generate()
        # 为了防止重复
        print('before:', len(case_list))
        no_repeat_case_list = []
        for one in case_list:
            if one not in no_repeat_case_list:
                no_repeat_case_list.append(one)
        print('after', len(no_repeat_case_list))
        return basic_case_list, no_repeat_case_list


def parameters_info_jike(parameters_data):
    if "fields" in parameters_data[0]:
        parameters_list = jsonpath.jsonpath(parameters_data, "$[0].fields.Parameter")[0]
        parameters_dict = {}
        son = {}
        for item in parameters_list:
            if not fnmatch(item["field"], '*' + '.' + '*'):
                parameters_dict.update({item["field"]: {"required": not item["optional"], "type": item["type"]}})
                # 还需要处理enum和二级json
                if "allowedValues" in item:
                    for index, each in enumerate(item["allowedValues"]):
                        item["allowedValues"][index] = each.strip('\'\"').strip('\"\'')
                    parameters_dict[item["field"]].update({"enum": item["allowedValues"]})
            else:
                father = item["field"].split(".")[0]
                son.update({item["field"].split(".")[1]: {"required": not item["optional"], "type": item["type"]}})
                if "allowedValues" in item:
                    for index, each in enumerate(item["allowedValues"]):
                        item["allowedValues"][index] = each.strip('\'\"').strip('\"\'')
                    son[item["field"].split(".")[1]].update({"enum": item["allowedValues"]})
        if son != {}:
            parameters_dict[father].update({"son": son})
    else:
        parameters_dict = {}
    return parameters_dict


def parameters_info_swagger(params, parameters, son_json, father):
    required = params['required']
    param_type = params['type']
    enum = []
    if 'enum' in params:
        enum = params['enum']
    elif 'Enum' in params:
        enum = params['Enum']
    parameters, son_json, father = collect_enum_and_json(parameters, params['name'], son_json,
                                                                  required, param_type, enum, father)
    return parameters, son_json, father


def body_info_swagger(params, json_data, body, son_json, father):
    # 要先从schema里取出ref（body的结构要去另一处找，这段结构里面只提供了ref）
    schema = params['schema']
    if '$ref' in schema:
        ref = schema['$ref']
        ref = ref.split('/')[-1]
        if ref == 'null':
            body = {}
        else:
            definitions_data = json_data['definitions']
            refs_data = definitions_data[ref]
            # 取出每一个然后加上是否required和type
            for each in refs_data['properties']:
                required = False
                if 'required' in refs_data:
                    if each in refs_data['required']:
                        required = True
                param_data = refs_data['properties'][each]
                try:
                    param_type = param_data['type']
                except KeyError:
                    param_type = 'string'
                # 如果是enum
                enum = []
                if 'enum' in param_data:
                    enum = param_data['enum']
                elif 'Enum' in param_data:
                    enum = param_data['Enum']

                parameters, son_json, father = collect_enum_and_json(body, each, son_json, required,
                                                                              param_type, enum, father)
        return body, son_json, father
    else:
        properties = schema['properties']
        for prop in properties:
            required = False
            if 'required' in properties[prop]:
                required = properties[prop]['required']
            try:
                param_type = properties[prop]['type']
            except KeyError:
                param_type = 'string'
            # 如果是enum
            enum = []
            if 'enum' in properties[prop]:
                enum = properties[prop]['enum']
            elif 'Enum' in properties[prop]:
                enum = properties[prop]['Enum']
            print('required:', required, 'type:', type(required))
            parameters, son_json, father = collect_enum_and_json(body, prop, son_json, required,
                                                                          param_type, enum, father)
    return body, son_json, father


def collect_enum_and_json(parameters, name, son_json, required, param_type, enum, father):
    """
    拼凑 enum 和二级 json
    :param parameters: 组织好的字典，参数-参数信息
    :param name: 参数名称
    :param son_json: 参数中的二级json
    :param required: 是否必要参数
    :param param_type: 参数类型
    :param enum: 参数enum取值范围
    :param father: 二级参数对应的父级参数
    :return:
    """
    param_name = name.lower()
    if len(enum) == 0 and (not fnmatch(param_name, '*' + '.' + '*')):
        parameters.update({name: {'required': required, 'type': param_type}})
    elif len(enum) > 0:
        parameters.update({name: {'required': required, 'type': param_type, 'enum': enum}})
    # 如果存在参数 xxx.xxx 那说明传参里有2级json，那要特殊处理一下
    elif fnmatch(param_name, '*' + '.' + '*'):
        father = name.split('.')[0]
        son = name.split('.')[1]
        son_json.update({son: {'required': required, 'type': param_type}})
    return parameters, son_json, father
