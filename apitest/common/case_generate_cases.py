# coding:utf-8
import itertools


class CaseGenerate:
    basic_case = []
    _400_case1 = []
    _400_case2 = []
    _400_case = []
    ok_case = []

    '''
    处理好的json格式参考：
    {
        "url": "/1.0/goodsNews/search",
        "method": "post",
        "parameters": {
        },
        "body": {
          "limit": {
            "required": true,
            "type": "integer"
          },
          "loadMoreKey": {
            "required": false,
            "type": "integer"
          },
          "text": {
            "required": true,
            "type": "string"
          }
        }
      },
      {
        "url": "/2.0/goods/detail",
        "method": "get",
        "parameters": {
          "id": {
            "required": true,
            "type": "string"
          },
          "platformType": {
            "required": true,
            "type": "string",
            "enum": ["xxx","xxxx"]
          },
          "location": {
            "required": true,
            "type": "string",
            "son": {"xxx": "xxxx", "xxx":"xxxx"}
          }
        },
        "body": {
        }
      }
    '''

    def __init__(self, case_name, url, method, parameters, body):
        self.case_name = case_name
        self.url = url
        self.method = method
        self.parameters = parameters
        self.body = body

    def generate(self):
        self.basic_case.append([self.case_name, self.url, self.method, self.parameters, self.body, 200])
        self.miss_unrequired()
        self.miss_required()
        all_case = self.basic_case + self.ok_case + self._400_case
        return all_case

    def miss_unrequired(self):
        """
        去除所有非必填参数，作为一条用例
        :return:
        """
        parameters, has_unrequired = del_unrequired_params(self.parameters)
        body, has_unrequired = del_unrequired_params(self.body)
        if has_unrequired:
            self.ok_case.append([self.case_name, self.url, self.method, parameters, body, 200])
        return self.ok_case

    def miss_required(self):
        """
        统计有多少个required，有n个就会生成n个case，每个case少一个必要参数
        :return:
        """
        if self.parameters:
            self.data_trans(which_part=self.parameters, serial=3)
        if self.body:
            self.data_trans(which_part=self.body, serial=4)

        self._400_case = self._400_case1 + self._400_case2
        return self._400_case

    def data_trans(self, which_part, serial):
        """
        去掉内容中的一个必要参数，形成 N 条用例，N = 必要参数的个数
        :param which_part:
        :param serial: 是 3 就代表是parameter，4 就代表body
        :return:
        """
        required_count = 0  # required_count 是必要参数的数量
        for each in which_part:
            if which_part[each]['required']:
                required_count += 1
        if required_count > 0:
            # 得到的是body中所有参数的一个排列组合（准确地说是body中key值的排列组合，每一个项都是元组格式
            parameters_list = list(itertools.combinations(which_part, len(which_part) - 1))
            for params_combo in parameters_list:
                required_count_in_combo = 0
                temp = {}
                for params in params_combo:
                    if which_part[params]['required']:
                        required_count_in_combo += 1
                if not params_combo:
                    if serial == 3:
                        self._400_case1.append([self.case_name, self.url, self.method, {}, self.body, 400])
                    else:
                        self._400_case2.append([self.case_name, self.url, self.method, self.parameters, {}, 400])
                if required_count_in_combo == required_count - 1 and params_combo:
                    for index, item in enumerate(list(params_combo)):
                        if 'enum' in which_part[params_combo[index]]:
                            temp.update({params_combo[index]: {'required': which_part[item]['required'],
                                                               'type': which_part[item]['type'],
                                                               'enum': which_part[item]['enum']}})
                        else:
                            if 'son' in which_part[params_combo[index]]:
                                temp.update({params_combo[index]: {'required': which_part[item]['required'],
                                                                   'type': which_part[item]['type'],
                                                                   'son': which_part[item]['son']}})
                            else:
                                temp.update({params_combo[index]: {'required': which_part[item]['required'],
                                                                   'type': which_part[item]['type']}})
                    if serial == 3:
                        self._400_case1.append([self.case_name, self.url, self.method, temp, self.body, 400])
                    else:
                        self._400_case2.append([self.case_name, self.url, self.method, self.parameters, temp, 400])


def del_unrequired_params(parameters):
    """
    去除内容中的非必要参数
    :param parameters:
    :return: 返回去除后的内容（不对入参做改变）
    """
    params = parameters.copy()
    has_unrequired = False
    if parameters:
        for each in parameters:
            if parameters[each]['required'] is False:
                del params[each]
                has_unrequired = True
    return params, has_unrequired
