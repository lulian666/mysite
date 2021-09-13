# coding:utf-8
import os
from fnmatch import fnmatch
import json

import jsonpath

from apitest.common.case_generate_cases import CaseGenerate


class CaseCollect:
    """
    排除一些不需要测试的接口（在前端输入），比如内部接口以及一些无法测试的比如绑定微信等
    这里包括了橙、快鸟、即刻夸夸和小宇宙的
    快鸟和即刻夸夸用了 swagger，但是却依旧有细节上的不同
    即刻夸夸和小宇宙都用的是即刻 api doc
    """
    root = os.path.abspath('.')  # 获取当前工作目录路径
    filepath = os.path.join(root, 'apitest/config/temp.json')

    def collect_data_accordingly(self, api_not_wanted, product_id):
        """
        根据项目来选择对应的解析方式
        :param api_not_wanted: 前端传入的参数，表示不需要测试的接口，string 类型，每个 url 之间以逗号隔开
        :param product_id: 项目 ID
        :return: 返回的 basic_case_list 是正向用例，case_list 是经过初步扩展的
        """
        if api_not_wanted:
            api_not_wanted = api_not_wanted.split(',')
        with open(self.filepath, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
        if product_id in ['1', '3']:  # 1和3分别代表橙和即刻夸夸项目
            print('按即刻接口文档格式解析')
            basic_case_list, case_list = self.collect_data_jike(json_data, api_not_wanted)
        elif product_id in ['4']:
            print('按小宇宙接口文档格式解析')
            basic_case_list, case_list = self.collect_data_podcast(json_data, api_not_wanted)
        else:
            # paths = json_data['paths']
            print('按 swagger 文档格式解析')
            basic_case_list, case_list = self.collect_data_jike(json_data, api_not_wanted)
        return basic_case_list, case_list

    @staticmethod
    def collect_data_podcast(json_data, api_not_wanted):
        # 小宇宙json文档待优化，先不解析
        basic_case_list, case_list = [], []
        # 小宇宙的文档结构，是同一个功能的都放在一个结构里，json_data 里的每个都可能包含不止一个 api
        # for apis in json_data:
        #     if 'item' in apis:
        #         for api in apis['item']:
        #             parameters, body = {}, {}
        #             url, method, case_name = '', '', ''
        #             if 'url' in str(api):
        #                 url = jsonpath.jsonpath(api, "$.url")[0]
        return basic_case_list, case_list

    @staticmethod
    def collect_data_swagger(json_data, paths, api_not_wanted):
        basic_case_list, case_list = [], []
        for path_key, path_value in paths.items():
            url = path_key
            for method_key, method_value in path_value.items():
                method = method_key
                case_wanted = is_case_wanted(url, api_not_wanted)
                # 有一些废弃的接口，也要排除一下
                deprecated = get_value_with_default(path_value.get(method), '$.deprecated', default=False)
                if case_wanted and not deprecated:
                    case_name = get_value_with_default(method_value, '$.summary', default='没有找到接口名称')
                    parameters_wanna_be = get_value_with_default(method_value, '$.parameters', default={})
                    parameters, body = delt_with_detail_info(parameters_wanna_be, json_data)
                    basic_case_list.append([case_name, url, method, parameters, body])
                    case_list = CaseGenerate(case_name, url, method, parameters, body).generate()
        return basic_case_list, case_list

    @staticmethod
    def collect_data_jike(json_data, interfaces_not_wanted):
        basic_case_list, case_list = [], []
        for api in json_data:
            parameters, body = {}, {}
            url = get_value_with_default(api, '$.url', default='')
            case_wanted = is_case_wanted(url, interfaces_not_wanted)
            if case_wanted:
                method = get_value_with_default(api, '$.type', default='')
                case_name = get_value_with_default(api, '$.title', default='')
                parameters_data = get_value_with_default(api, '$.parameter', default={})
                if parameters_data:
                    if method.lower() == 'post':
                        body = parameters_info_jike(parameters_data)
                    else:
                        parameters = parameters_info_jike(parameters_data)
                else:
                    parameters, body = {}, {}
                if url:
                    basic_case_list.append([case_name, url, method, parameters, body])
                    case_list = CaseGenerate(case_name, url, method, parameters, body).generate()
        return basic_case_list, case_list


def parameters_info_jike(parameters_data):
    """
    获取参数和 body 信息
    :param parameters_data:
    :return:
    """
    if 'fields' in parameters_data:
        parameters_list = get_value_with_default(parameters_data, '$.fields.Parameter', default=[])
        parameters_dict, son = {}, {}
        for item in parameters_list:
            if not fnmatch(item['field'], '*' + '.' + '*') and item['field'].lower() != 'loadmorekey':
                parameters_dict.update({item['field']: {'required': not item['optional'], 'type': item['type']}})
                # 还需要处理 enum 和二级 json
                add_allowed_values(item, parameters_dict[item['field']])
            elif fnmatch(item['field'], '*' + '.' + '*') and item['field'].split('.')[0].lower() != 'loadmorekey':
                father = item['field'].split('.')[0]
                son.update({item['field'].split('.')[1]: {'required': not item['optional'], 'type': item['type']}})
                add_allowed_values(item, son[item['field'].split('.')[1]])
        if son != {}:
            parameters_dict[father].update({'son': son})
    else:
        parameters_dict = {}
    return parameters_dict


def delt_with_detail_info(parameters_wanna_be, json_data):
    """
    处理参数的细节
    :param parameters_wanna_be:
    :param json_data:
    :return: 返回字典格式的 参数和 body
    """
    if parameters_wanna_be:  # 如果有 parameters 的话，有的接口是没有的
        parameters, body, son_json, father = {}, {}, {}, ''
        for params in parameters_wanna_be:
            if params['in'] in ['query', 'path']:  # 代表是 parameters
                parameters, son_json, father = parameters_info_swagger(params, parameters, son_json, father)
            else:  # 如果是body的话
                body, son_json, father = body_info_swagger(params, json_data, body, son_json, father)
        # 用来处理参数中 2 级 json
        json_in_parameters(parameters, father, son_json)
        json_in_parameters(body, father, son_json)
    else:
        parameters = {}
        body = {}
    return parameters, body


def parameters_info_swagger(params, parameters, son_json, father):
    """
    获取参数信息
    :param params:
    :param parameters:
    :param son_json:
    :param father:
    :return:
    """
    required = params['required']
    param_type = params['type']
    enum = []
    if 'enum' in params:
        enum = params['enum']
    elif 'Enum' in params:
        enum = params['Enum']
    parameters, son_json, father = collect_enum_and_json(parameters, params['name'], son_json, required, param_type, enum, father)
    return parameters, son_json, father


def body_info_swagger(params, json_data, body, son_json, father):
    """
    获取 body 信息
    :param params:
    :param json_data:
    :param body:
    :param son_json:
    :param father:
    :return:
    """
    # 要先从 schema 里取出 ref（body 的结构要去另一处找，这段结构里面只提供了 ref）
    schema = params['schema']
    if '$ref' in schema:
        ref = schema['$ref'].split('/')[-1]
        definitions_data = json_data['definitions']
        refs_data = definitions_data[ref]
        # 取出每一个然后加上是否 required 和 type
        for each in refs_data['properties']:
            required = False
            if 'required' in refs_data:
                if each in refs_data['required']:
                    required = True
            param_type, enum = get_type_and_required(refs_data['properties'][each])
            parameters, son_json, father = collect_enum_and_json(body, each, son_json, required, param_type, enum, father)
        return body, son_json, father
    else:
        properties = schema['properties']
        for prop in properties:
            required = False
            if 'required' in properties[prop]:
                required = properties[prop]['required']
            param_type, enum = get_type_and_required(properties[prop])
            parameters, son_json, father = collect_enum_and_json(body, prop, son_json, required, param_type, enum, father)
    return body, son_json, father


def collect_enum_and_json(parameters, name, son_json, required, param_type, enum, father):
    """
    拼凑 enum 和二级 json，参数名称为 loadMoreKey 时也不保存，因为自动生成用例时无法知道 loadMoreKey 是什么值
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
    if not enum and (not fnmatch(param_name, '*' + '.' + '*')) and param_name != 'loadmorekey':
        parameters.update({name: {'required': required, 'type': param_type}})
    elif enum and param_name != 'loadmorekey':
        parameters.update({name: {'required': required, 'type': param_type, 'enum': enum}})
    # 如果存在参数 xxx.xxx 那说明传参里有2级json，那要特殊处理一下
    elif fnmatch(param_name, '*' + '.' + '*') and param_name != 'loadmorekey':
        father, son = name.split('.')
        son_json.update({son: {'required': required, 'type': param_type}})
    return parameters, son_json, father


def is_case_wanted(url, api_not_wanted):
    """
    判断 url 是否在 api_not_wanted 中，如果在表示此 接口被设置为不需要测试
    :param url: 接口的 url
    :param api_not_wanted: 不测试的接口的 list
    :return:
    """
    case_wanted = True
    if api_not_wanted:
        for each in api_not_wanted:
            if fnmatch(url, '*' + each + '*'):
                case_wanted = False
    return case_wanted


def json_in_parameters(parameters, father, son_json):
    """
    处理 json 格式的参数
    :param parameters:
    :param father:
    :param son_json:
    :return:
    """
    for item in parameters:
        if item == father:
            parameters[item].update({'son': son_json})


def get_type_and_required(param_data):
    """
    获取 type 和 enum 信息
    :param param_data:
    :return: 返回一个字符串和列表，找不到的话默认 string 和空列表
    """
    try:
        param_type = param_data['type']
    except KeyError:
        param_type = 'string'
    try:
        enum = param_data['enum']
    except KeyError:
        enum = []
    return param_type, enum


def get_value_with_default(dic, json_path, default):
    """
    从 json 中取得相应的值，没找到就用默认参数 default
    :param dic:
    :param json_path:
    :param default:
    :return:
    """
    value_list = jsonpath.jsonpath(dic, json_path)
    if not value_list:
        value = default
    else:
        value = value_list[0]
    return value


def add_allowed_values(item, parameters_dict):
    """
    把内容中的 allowedValues 取出来（注意文档中的值都多了个双引号）
    :param item:
    :param parameters_dict:
    :return:
    """
    if 'allowedValues' in item:
        for index, each in enumerate(item['allowedValues']):
            item['allowedValues'][index] = each.strip('\'\"').strip('\"\'')
        parameters_dict.update({'enum': item['allowedValues']})
