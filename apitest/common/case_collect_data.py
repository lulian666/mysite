# coding:utf-8
import os
from fnmatch import fnmatch
import json

import jsonpath

from apitest.common.case_generate_cases import CaseGenerate


class CaseCollect:
    # 排除一些不需要测试的接口，比如内部接口，比如需要具体id的，但是id会过期的（商品id，卡片id），以及一些无法测试的比如绑定微信等
    # 这里包括了橙和快鸟的
    basic_case_list = []
    interfaces_not_wanted = ['internal', 'advertisement', 'promotion', 'user/miniProgram', 'user/qq', 'user/taobao',
                                 'user/wechat', 'management', 'newsBot', 'userRelation/unbind', 'user/cancel',
                                 'user/deviceId', 'user/pushToken', '2.0/transaction/withdraw',
                                 '2.0/goodsNews/read/report', '/userRelation/validFans/count', 'user/bindTpwd',
                                 'user/fans/invite', 'user/sms/bind', 'user/sms/loginOrSignup', 'goodsNews/content/paginate',
                                 'goodsNews/delete', '2.0/goodsNews/activity/promotion', 'orderShare/accept',
                                 '3.0/goodsNews', '2.0/goodsNews/sh','2.0/goods/promotionCount','2.0/goods/detai',
                                 '2.0/goods/promotion','userMonitor/templateId/upload','/userMonitor/delete','userMonitor/delete',
                                 '1.0/account/sms/loginOrSignUp','1.0/match/like','1.0/match/view','1.0/profile/avatarComparison',
                                 '1.0/profile/deletePhoto','1.0/profile/protestAvatarComparison','1.0/profile/uploadAvatar',
                                 '1.0/report/message','1.0/report/user','1.0/questionnaires/create','1.0/account/toggleGhostMode',
                                 '1.0/account/device/update','1.0/account/token/update','1.0/charges/create','1.0/charges/validateIAPReceipt',
                                 '/1.0/draw/','/1.0/im/message/exchangeWechat','1.0/im/interaction/pat','1.0/im/conversation/break',
                                 '/1.0/im/conversation/get','1.0/im/suggestion/get','1.0/im/message/list','1.0/im/conversation/read',
                                 '1.0/im/message/requestFillingSocialActivities','1.0/im/conversation/restart','1.0/im/message/send',
                                 '1.0/match/getSingleCard','1.0/match/dislike','1.0/orders/create','1.0/account/email/loginOrSignUp',
                                 '1.0/im/message/exchangeWechat','1.0/im/conversation/get','1.0/account/requestCancellation',
                                 '1.0/draw/drawPrize','1.0/draw/drop','comment/creat','user/sms/unbin']
    root = os.path.abspath('.')  # 获取当前工作目录路径
    filepath = os.path.join(root, 'apitest/config/temp.json')

    # 这里会删除所有老的case，把新的case写进数据库里面
    def collect_data_swagger(self):
        json_data, path_data = file_data(self.filepath)

        # 如果不照着json文件看，可能会理解上有困难
        for path_keys in path_data:
            url = path_keys
            method = list(path_data[url].keys())[0]
            case_wanted = True

            for each in self.interfaces_not_wanted:
                if fnmatch(url, '?' + each + '*'):
                    case_wanted = False
            # 有一些废弃的接口，也要排除一下
            if 'deprecated' in path_data[url].get(method):
                deprecated = path_data[url].get(method).get('deprecated')
                if deprecated is True:
                    case_wanted = False

            # 此外，还要兼容没有这个字段的时候（比如快鸟有，橙没有）
            # 很烦人的是有时候method大小写还不一致，有时候是post，有时候是POST……也要处理一下
            if case_wanted:
                for path_values in path_data[url]:
                    other_info = path_data[url][method]
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
                                parameters[item].update({'son': son_json})
                        for item in body:
                            if item == father:
                                body[item].update({'son': son_json})
                    else:
                        parameters = {}
                        body = {}

                self.basic_case_list.append([url, method, parameters, body])
                case_list = CaseGenerate(url, method, parameters, body).generate()
        print('总共多少case：', len(case_list))
        return self.basic_case_list, case_list

    def collect_data_jike(self):
        with open(self.filepath, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

        for api in json_data:
            url = jsonpath.jsonpath(api, "$.url")[0]
            method = jsonpath.jsonpath(api, "$.type")[0]
            if "parameter" in api:
                parameters_data = jsonpath.jsonpath(api, "$.parameter")
            else:
                parameters_data = {}
            if parameters_data != {}:
                if method.lower() == "post":
                    body = parameters_info_jike(parameters_data)
                else:
                    parameters = parameters_info_jike(parameters_data)
            else:
                parameters = {}
                body = {}
            self.basic_case_list.append([url, method, parameters, body])
            print([url, method, parameters, body])
            print("-----------------")
            case_list = CaseGenerate(url, method, parameters, body).generate()
        print("基本case有几个：", len(self.basic_case_list))
        print('总共多少case：', len(case_list))
        return self.basic_case_list, case_list


def parameters_info_jike(parameters_data):
    if "fields" in parameters_data[0]:
        parameters_list = jsonpath.jsonpath(parameters_data, "$[0].fields.Parameter")[0]
        parameters_dict = {}
        son = {}
        for item in parameters_list:
            if not fnmatch(item["field"], '*' + '.' + '*'):
                parameters_dict.update({item["field"]: {"required": not item["optional"], "type": item["type"]}})
                # 还需要处理enum和二级json
            else:
                father = item["field"].split(".")[0]
                son.update({item["field"].split(".")[1]: {"required": not item["optional"], "type": item["type"]}})
            if "allowedValues" in item:
                parameters_dict[item["field"]].update({"enum": item["allowedValues"]})
        if son != {}:
            parameters_dict[father].update({"son": son})
    else:
        parameters_dict = {}
    return parameters_dict


def file_data(filepath):
    # 第一步，拉取数据
    with open(filepath, 'r', encoding='utf8')as fp:
        json_data = json.load(fp)
        try:
            path_data = json_data['paths']
        except TypeError:
            path_data = json_data
    return json_data, path_data


def parameters_info_swagger(params, parameters, son_json, father):
    required = params['required']
    param_type = params['type']
    enum = []
    if 'enum' in params:
        enum = params['enum']
    elif 'Enum' in params:
        enum = params['Enum']
    parameters, son_json, father = exclude_loadmorekey_and_avatar(parameters, params['name'], son_json,
                                                                  required, param_type, enum, father)
    return parameters, son_json, father


def body_info_swagger(params, json_data, body, son_json, father):
    # 要先从schema里取出ref（body的结构要去另一处找，这段结构里面只提供了ref）
    schema = params['schema']
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
            param_type = param_data['type']
            # 如果是enum
            enum = []
            if 'enum' in param_data:
                enum = param_data['enum']
            elif 'Enum' in param_data:
                enum = param_data['Enum']

            parameters, son_json, father = exclude_loadmorekey_and_avatar(body, each, son_json, required,
                                                                          param_type, enum, father)
    return body, son_json, father


def exclude_loadmorekey_and_avatar(parameters, name, son_json, required, param_type, enum, father):
    """
    橙的部分参数是loadMoreKey.xxxx，这些都统一不处理，哦还有avatarFile，不想搞
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
    if ((not fnmatch(param_name, 'loadmorekey' + '*')) and param_name != 'avatarFile') and len(enum) == 0 and (not fnmatch(param_name, '*' + '.' + '*')):
        parameters.update({name: {'required': required, 'type': param_type}})
    elif ((not fnmatch(param_name, 'loadmorekey' + '*')) and param_name != 'avatarFile') and len(enum) > 0:
        parameters.update({name: {'required': required, 'type': param_type, 'enum': enum}})
    # 如果存在参数 xxx.xxx 那说明传参里有2级json，那要特殊处理一下
    elif (not fnmatch(param_name, 'loadmorekey' + '*')) and fnmatch(param_name, '*' + '.' + '*'):
        father = name.split('.')[0]
        son = name.split('.')[1]
        son_json.update({son: {'required': required, 'type': param_type}})
    return parameters, son_json, father
