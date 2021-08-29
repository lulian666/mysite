# coding:utf-8
import copy

from apitest.common.read_config import Read_config

'''
这个类用来把生成case准备好：
data_form()用来把body和parameter参数变成格式: {'paramA': 'xxx', 'paramB': 'xxx'}
data_replace()用来替换参数里面的具体值，它依赖于参数规则
enum_data()把接口参数里的enum给整好
'''


class CaseReady:
    def data_form(self, product_id, parameter_index, body_index, case_list, variable_list):
        n = 0
        new_case_list = []
        # 其实就是把{"required": false, "type": "string"} 这部分替换成真正的值
        for case in case_list:
            n += 1
            if case[body_index] != {}:  # 处理body的
                self.enum_data(case[body_index], n, case, new_case_list, body_index, product_id, case_list, variable_list)
            elif case[parameter_index] != {}:
                # 处理parameters的
                self.enum_data(case[parameter_index], n, case, new_case_list, parameter_index, product_id, case_list, variable_list)
            else:
                # 如果body和param都是空的，那就直接变成case
                new_case_list.append(case_list[n-1])
        return new_case_list  # 这个list是最终的case

    def enum_data(self, case, n, case_full_info, new_case_list, nn, product_id, case_list, variable_list):
        # 这个方法是处理接口参数里的enum
        para_info_list = list(case.values())  # 这个list里的每一个值都是个dict
        para_list = list(case.keys())

        enum_count = 0
        enum_dict = {}
        for info in para_info_list:
            param = para_list[para_info_list.index(info)]
            if 'enum' in info:
                enum_count += 1
                # 这里顺便把哪几个参数类型是enum的找出来
                enum_list1 = info['enum']
                enum_dict.update({param: enum_list1})
            if 'son' in info:
                case[param] = info['son']
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
        if not enum_count:  # 参数里面没有enum类型的时候，只要正常替换参数就好
            # 这里就该处理二级json里面有enum的情况，太复杂了，处理不好，苏哪里
            # if 'enum' in str(case):
            #     # 这里我只处理只有1个enum的情况，有2个的去死吧……
            #     for param in case:
            #         if 'enum' in str(case[param]):
            #             case_param_list = {}
            #             value = ''
            #             print('here case[param]:', case[param])
            #             for key, value in case[param].items():
            #                 if 'enum' in value:
            #                     enum_list2 = case[param]['enum']
            #                     for enum in enum_list2:
            #                         case_param_list.update({key: enum})
            #
            #         else:
            #             value = self.data_replace(param, case[param], product_id, case_full_info[1], variable_list)  # 二级json的逻辑都在data_replace里处理（不包含耳机里面还有enum的情况）
            #         case[param] = value
            # else:
            #     for param in case:
            #         # print('there')
            #         value = self.data_replace(param, case[param], product_id, case_full_info[1], variable_list)  # 二级json的逻辑都在data_replace里处理（不包含耳机里面还有enum的情况）
            #         case[param] = value
            #     new_case_list.append(copy.deepcopy(case_list[n - 1]))
            for param in case:
                value = self.data_replace(param, case[param], product_id, case_full_info[1], variable_list)  # 二级json的逻辑都在data_replace里处理（不包含耳机里面还有enum的情况）
                case[param] = value
            new_case_list.append(copy.deepcopy(case_list[n - 1]))

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
                        # 当我再次看到这里的时候，我已经不记得这些参数是什么意思了，但不妨碍我进行修改
                        new_case_m.update({param: self.data_replace(param, case[param], product_id, case_full_info[1], variable_list)})
                if nn == 4:
                    new_case_list.append([case_full_info[0], case_full_info[1], case_full_info[2], case_full_info[3], new_case_m, case_full_info[5]])
                elif nn == 3:
                    new_case_list.append([case_full_info[0], case_full_info[1], case_full_info[2], new_case_m, case_full_info[4], case_full_info[5]])

        if enum_count == 1:
            for param in case:
                if 'enum' in case[param]:
                    enum = case[param]['enum']
                    how_many = len(enum)
                    for enum_value in enum:
                        new_case_list.append(copy.deepcopy(case_list[n - 1]))
                        # 这里加一个判断，如果 type 是 string[] 类型，赋值应该是["xxx"]
                        if case[param]['type'] == 'String[]':
                            new_case_list[-1][nn][param] = [enum_value]
                        else:
                            new_case_list[-1][nn][param] = enum_value
            for item in new_case_list[-how_many:]:  # 这里终于对了
                for param in item[nn]:
                    if 'type' in item[nn][param]:
                        value = self.data_replace(param, item[nn][param], 2, case_full_info[1], variable_list)
                        item[nn][param] = value

    @staticmethod
    def data_replace(param, param_value, product_id, api, variable_list):
        """
        这个方法是制定了一系列复杂的规则，以替换参数的值（其实也不复杂）
        :param param: 变量的名称
        :param param_value: 变量的内容
        :param product_id: 项目id
        :param api: 完整case信息
        :param variable_list: 变量列表
        :return: 
        """
        # 二级json来了，为什么是这个判断条件，是因为如果是二级的话，她的字典值的某个字典值也是字典（绕口令了）
        if param_value != '' and isinstance(list(param_value.values())[0], dict):
            cp_param_value = copy.deepcopy(param_value)
            for index, item in enumerate(param_value):
                # 这里别把son里面的enum丢了
                if 'enum' in param_value[item]:
                    # 这里就有点麻烦，先默认enum可选值只有一个
                    item_value = param_value[item]['enum'][0]
                else:
                    item_value = Read_config().get_variable(variable_list, product_id, api, item)
                cp_param_value[item] = item_value
            return cp_param_value  # 直接返回一个dict
        else:
            value = Read_config().get_variable(variable_list, product_id, api, param)
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
