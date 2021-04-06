# coding:utf-8
import itertools

'''
这个类用来生成不同情况的case
把case汇集到一个list里面
generate()是最基础的，return basic_case
miss_unrequired()是去掉所有非必要参数，return ok_case
miss_required()是去掉一个必要参数，return _400_case
'''
class Case_generate:
    #怎么感觉这里的写法还是java啊
    basic_case = []
    _400_case1 = []
    _400_case2 = []
    _400_case = []
    ok_case = [] #只保留required参数的，没想到好的命名

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
    def __init__(self, url, method, parameters, body):
        self.url = url
        self.method = method
        self.parameters = parameters
        self.body = body

    def generate(self):
        self.basic_case.append([self.url, self.method, self.parameters, self.body,200])
        self.miss_unrequired()
        self.miss_required()
        all_case = self.basic_case + self.ok_case + self._400_case
        return all_case


    #少传一个非必要参数，就是把所有非必要参数都去掉
    '''啊啊啊啊啊这里有重复的case啊啊啊啊啊！！！！
        修好了嘻嘻
    '''
    def miss_unrequired(self):
        body = self.body.copy()
        parameters = self.parameters.copy()
        has_unrequired = False
        if self.parameters != {}:
            for each in self.parameters:
                if self.parameters[each]['required'] is False:
                    del parameters[each]
                    has_unrequired = True
        if self.body != {}:
            for each in self.body:
                if self.body[each]['required'] is False:
                    del body[each]
                    has_unrequired = True
        if has_unrequired: #如果没有unrequired的就不生成case了，避免和basic_case重复
            self.ok_case.append([self.url, self.method, parameters, body,200])
        return self.ok_case

    # 统计有多少个required，有n个就会生成n个case，每个case少一个必要参数
    def miss_required(self):
        if len(self.parameters) > 0:
            self.data_trans(self.parameters,2)
        if len(self.body) > 0:
            self.data_trans(self.body, 3)

        self._400_case = self._400_case1 + self._400_case2
        return self._400_case

    def data_trans(self, whichpart, serial):
        #serial是2就代表是parameter，3就代表body
        m = 0  # m是必要参数的数量
        for each in whichpart:
            if whichpart[each]['required'] is True:
                m += 1
        if m > 0:
            # 得到的是body中所有参数的一个排列组合（准确地说是body中key值的排列组合
            parameters_list = list(itertools.combinations(whichpart, len(whichpart) - 1))
            for params_combi in parameters_list:
                n = 0
                temp = {}
                for params in params_combi:
                    if whichpart[params]['required'] is True:
                        n += 1
                if len(params_combi) == 0:
                    if serial == 2:
                        self._400_case1.append([self.url, self.method, {}, self.body, 400])
                    else:
                        self._400_case2.append([self.url, self.method, self.parameters, {}, 400])
                if n == m - 1 and len(params_combi) != 0:
                    # 如果正好小1，那就是我们想要的case
                    # 需要把params_combi变回原来的格式
                    for i in range(len(params_combi)):
                        temp.update({params_combi[i]: {'required': whichpart[params_combi[i]]['required'],
                                                       'type': whichpart[params_combi[i]]['type']}})
                    if serial == 2:
                        self._400_case1.append([self.url, self.method, temp, self.body, 400])
                    else:
                        self._400_case2.append([self.url, self.method, self.parameters, temp, 400])