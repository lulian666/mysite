# coding:utf-8
import os
from fnmatch import fnmatch
import json

from apitest.common.case_generate_cases import Case_generate
from apitest.common.case_readyfortest import Case_ready


class Case_collect:
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

    # def __init__(self, json_path):
    #     # 读取json文件内容,返回字典格式
    #     self.json_path = json_path
        # self.case_list = []
        # self.variable_list = variable_list

    # 这里会删除所有老的case，把新的case写进数据库里面
    def collect_data(self):
        n = 0 #忽略，debug用的
        root = os.path.abspath('.') #获取当前工作目录路径
        filepath = os.path.join(root, 'apitest/config/temp.json')
        print(filepath)

        #第一步，拉取数据
        with open(filepath, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
            path_data = json_data['paths']

        #如果不照着json文件看，可能会理解上有困难
        for path_keys in path_data: #json_data['paths']是取到了json_data这个字典里面所有paths的值
            url = path_keys
            # print('url:',url)
            case_wanted = True #用来标记这个接口是不是需要测
            for each in self.interfaces_not_wanted:
                if fnmatch(url,'?' + each + '*'):
                    case_wanted = False
            #有一些废弃的接口，也要排除一下
            #此外，还要兼容没有这个字段的时候（比如快鸟有，橙没有）
            #很烦人的是有时候method大小写还不一致，有时候是post，有时候是POST……也要处理一下
            method = list(path_data[url].keys())[0]
            if 'deprecated' in path_data[url].get(method):
                # deprecated = path_data[url].get('post').get('deprecated') if path_data[url].get('get') == None else path_data[url].get('get').get('deprecated')
                deprecated = path_data[url].get(method).get('deprecated')
                if deprecated is True:
                    case_wanted = False
            if case_wanted:
                for path_values in path_data[url]:
                    # 重新搞个数组吧，就叫other_info
                    other_info = path_data[url][method]
                    if 'parameters' in other_info:  # 如果有parameters的话，有的接口是没有的
                        parameters_maybe = other_info['parameters']
                        # 如果name是query的就表示是跟在url后的参数，如果不是就表示是body
                        parameters = {}
                        body = {}
                        father = ''
                        son_json = {}
                        for params in parameters_maybe:
                            if params['in'] == 'query' or params['in'] == 'path':  # 如果不是body就代表是parameters
                                required = params['required']
                                param_type = params['type']
                                enum = []
                                if 'enum' in params:
                                    enum = params['enum']
                                elif 'Enum' in params:
                                    enum = params['Enum']

                                # 橙的部分参数是loadMoreKey.xxxx，这些都统一不处理，哦还有avatarFile，不想搞
                                if ((not fnmatch(params['name'],'loadMoreKey' + '*')) and (not fnmatch(params['name'],'loadmorekey' + '*')) and params['name'] != 'avatarFile') and len(enum) == 0 and (not fnmatch(params['name'],'*' + '.' + '*')):
                                    parameters.update({params['name']: {'required': required, 'type': param_type}})
                                elif ((not fnmatch(params['name'],'loadMoreKey' + '*')) and (not fnmatch(params['name'],'loadmorekey' + '*'))and params['name'] != 'avatarFile') and len(enum) > 0:
                                    parameters.update({params['name']: {'required': required, 'type': param_type, 'enum': enum}})
                                #如果存在参数 xxx.xxx 那说明传参里有2级json，那要特殊处理一下（依旧要先排除是loadmorekey
                                elif ((not fnmatch(params['name'],'loadMoreKey' + '*')) and (not fnmatch(params['name'],'loadmorekey' + '*'))) and fnmatch(params['name'],'*' + '.' + '*'):
                                    father = params['name'].split('.')[0]
                                    son = params['name'].split('.')[1]
                                    son_json.update({son: {'required': required, 'type': param_type}})
                            else:  # 如果是body的话
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
                                        if 'required' in refs_data: # 有可能没有required
                                            if each in refs_data['required']:
                                                required = True
                                        param_data = refs_data['properties'][each]
                                        param_type = param_data['type']
                                        #如果是enum
                                        enum = []
                                        if 'enum' in param_data:
                                            enum = param_data['enum']
                                        elif 'Enum' in param_data:
                                            enum = param_data['Enum']

                                        if ((not fnmatch(each,'loadMoreKey' + '*')) and (not fnmatch(each,'loadmorekey' + '*'))and each != 'avatarFile') and len(enum)== 0 and (not fnmatch(each,'*' + '.' + '*')) :
                                            body.update({each: {'required': required, 'type': param_type}})
                                        elif ((not fnmatch(each,'loadMoreKey' + '*')) and (not fnmatch(each,'loadmorekey' + '*'))and each != 'avatarFile') and len(enum) > 0:
                                            body.update({each: {'required': required, 'type': param_type, 'enum': enum}})
                                        elif ((not fnmatch(each, 'loadMoreKey' + '*')) and (not fnmatch(each, 'loadmorekey' + '*'))) and fnmatch(each,'*' + '.' + '*'):
                                            father = each.split('.')[0]
                                            son = each.split('.')[1]
                                            son_json.update({son: {'required': required, 'type': param_type}})
                        # 这俩遍历是用来寻找参数中2级json的爸爸
                        for item in parameters:
                            if item == father:
                                parameters[item].update({'son':son_json})
                        for item in body:
                            if item == father:
                                body[item].update({'son':son_json})
                    else:  # 不需要任何参数的话，就全都空
                        parameters = {}
                        body = {}
                #先把数据变成一个数组把（第二步）
                self.basic_case_list.append([url, method, parameters, body])
                case_list = Case_generate(url, method, parameters, body).generate()
                n += 1  # 忽略，debug用的
        # for case in case_list:
        #     print('before', case)
        print('总共多少case：', len(case_list))  # 这个数字绝壁有毛病吧！
        # print('case_list from case_collect_data', case_list)

        #第三步，处理数据
        # case_list = Case_ready(case_list, self.variable_list).data_form

        return self.basic_case_list, case_list

# if __name__ == '__main__':
#     root = os.path.abspath('..') #获取当前工作目录路径
#     filepath = os.path.join(root, 'config/swagger.json')
#     print(filepath)
#     Case_collect(filepath).collect_data()