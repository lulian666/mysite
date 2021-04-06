# coding:utf-8
import copy
from random import Random

from read_config import Read_config

'''
这个类用来把生成case准备好：
data_form()用来把body和parameter参数变成格式: {'paramA': 'xxx', 'paramB': 'xxx'}
data_replace()用来替换参数里面的具体值，它依赖于参数规则
enum_data()把接口参数里的enum给整好
'''

class Case_ready:
    def __init__(self, case_list):
        self.case_list = case_list

    @property
    def data_form(self):
        n = 0
        new_case_list = [] #新建一个列表存case
        #其实就是把{"required": false, "type": "string"} 这部分替换成真正的值
        for case in self.case_list:
            n += 1
            print('case_original:',case)
            if case[3] != {}: #处理body的
                self.enum_data(case[3],n,case,new_case_list,3)
            elif case[2] != {}:
                #处理parameters的
                self.enum_data(case[2],n,case,new_case_list,2)
            else:
                #如果body和param都是空的，那就直接变成case
                new_case_list.append(self.case_list[n-1])
        for case in new_case_list:
            print('new_case：', case)
        return new_case_list

    def data_replace(self,param, param_value):
        # print(param,param_value)
        #这个方法是制定了一系列复杂的规则，以替换参数的值（其实也不复杂）
        if param == 'keyword':
            value = Random().randint(0,100000)
        elif len(param_value) > 2: #二级json来了
            for item in param_value:
                item_value = Read_config().get_value('PARAMETERS', item)
                param_value[item] = item_value
            return param_value #直接返回一个dict
        else:
            value = Read_config().get_value('PARAMETERS', param)
        return value

        '''
        二级json举例
        {
            'encore': {'required': False, 'type': 'boolean'}, 
            'location': {
                             'required': False, 
                             'type': 'object',
                             'son': {
                                        'lng': {'required': True, 'type': 'string'}, 
                                        'lat': {'required': True, 'type': 'string'},
                                        'coordType': {'required': True, 'type': 'string'}
                                    }
                         }
        }
        '''

    def enum_data(self,case,n,case_full_info,new_case_list,nn):

        #这个方法是处理接口参数里的enum
        para_info_list = list(case.values())  # 这个list里的每一个值都是个dict
        para_list = list(case.keys())
        enum_count = 0;
        enum_dict = {}
        for key in para_info_list:
            # print('key:',key)
            param = para_list[para_info_list.index(key)]
            # print('param:',param)
            if 'enum' in key:
                enum_count += 1
                # 这里顺便把哪几个参数类型是enum的找出来
                enum_list1 = key['enum']
                enum_dict.update({param: enum_list1})
            if 'son' in key:
                case[param] = key['son']

        '''
        上面处理完以后 会变成
        {
            'encore': {'required': False, 'type': 'boolean'}, 
            'location': {
                             'lng': {'required': True, 'type': 'string'}, 
                             'lat': {'required': True, 'type': 'string'},
                             'coordType': {'required': True, 'type': 'string'}
                        }         
        }                
        '''
        if enum_count == 0:  # 参数里面没有enum类型的时候，只要正常替换参数就好
            for param in case:
                value = self.data_replace(param,case[param]) #二级json的逻辑都在data_replace里处理
                case[param] = value
                # if 'type' in case[param]:
                #     value = self.data_replace(param, case[param]['type'])
                #     case[param] = value
            new_case_list.append(copy.deepcopy(self.case_list[n - 1]))

        if enum_count > 1:
            # 用到enum_dict
            enum_list = list(enum_dict.values())
            # 这里思路是把所有是enum的参数的可取值都列出来，然后排列组合
            # 最多需要多少个组合，比如有n个enum类型的参数，那应该就是enum个数最多的那个，假设是m
            # 就以m数字循环，每一个param的值等于enum里面的第i个，如果不存在则取第一个
            # 现确定m的值：
            m = 1
            for item in enum_list:
                if m < len(item):
                    m = len(item)
            for i in range(m):
                new_case_m = {}
                for param in case:
                    if param in enum_dict:
                        new_value = enum_dict[param][i] if i < len(enum_dict[param]) else enum_dict[param][0]
                        new_case_m.update({param: new_value})
                    else:
                        #当我再次看到这里的时候，我已经不记得这些参数是什么意思了，但不妨碍我进行修改
                        new_case_m.update({param: self.data_replace(param, case[param])})

                if nn == 3:
                    new_case_list.append([case_full_info[0], case_full_info[1], case_full_info[2], new_case_m, case_full_info[4]])
                elif nn == 2:
                    new_case_list.append([case_full_info[0], case_full_info[1], new_case_m, case_full_info[3], case_full_info[4]])

        if enum_count == 1:
            for param in case:
                if 'enum' in case[param]:
                    enum = case[param]['enum']
                    how_many = len(enum)
                    for enum_value in enum:
                        new_case_list.append(copy.deepcopy(self.case_list[n - 1]))
                        new_case_list[-1][nn][param] = enum_value
            for item in new_case_list[-how_many:]:  # 这里终于对了
                for param in item[nn]:
                    if 'type' in item[nn][param]:
                        value = self.data_replace(param, item[nn][param])
                        item[nn][param] = value


