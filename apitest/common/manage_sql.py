# coding:utf-8
import ast
import json

import pymysql

# list = [['/userRelation/fans/paginate', 'post', {}, {'limit': 10}, 400],
#         ['/user/favours/update', 'post', {}, {}, 400],
#         ['/userMonitor/message/search', 'get', {'limit': 10}, {}, 400],]
from apitest.common.case_test import Case_request


class Manage_sql:
    # def writeToSQL_singlecase(self):
    #     # sql = "update apitest_apis set apitest_apis.apiurl=%s, apitest_apis.apimethod=%s, apitest_apis.apiparamvalue=%s, apitest_apis.apibodyvalue=%s, apitest_apis.apiexpectstatus=%s"
    #     sql = "insert into apitest_apis(apiname,apiurl,apimethod,apiparamvalue,apibodyvalue,apiexpectstatus,Product_id) values(%s,%s,%s,%s,%s,%s,%s);"
    #     param = ('test', '/userRelation/fans/paginate', 'get', '{\'limit\': 10}', '{}', '400', '1')
    #     coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
    #     cursor = coon.cursor()
    #     cursor.execute(sql, param)
    #     coon.commit()
    #     cursor.close()
    #     coon.close()
    #     return

    def writeCaseToSQL(self, caselist):
        # sql = "update apitest_apis set apitest_apis.apiurl=%s, apitest_apis.apimethod=%s, apitest_apis.apiparamvalue=%s, apitest_apis.apibodyvalue=%s, apitest_apis.apiexpectstatus=%s"
        sql = "insert into apitest_apis(apiname,apiurl,apimethod,apiparamvalue,apibodyvalue,apiexpectstatuscode,Product_id) values(%s,%s,%s,%s,%s,%s,%s);"
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()

        # 这里开始循环写入表
        for case in caselist:
            print(case)
            param = ('test', case[0], case[1], case[2].__str__(), case[3].__str__(), case[4].__str__(), '2') #不转换成str会出错，因为值里面有引号
            cursor.execute(sql, param)
            coon.commit()

        cursor.close()
        coon.close()
        return

    def deleteCaseInSQL(self):
        sql = 'delete from apitest_apis'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        cursor.execute(sql)
        coon.commit()
        cursor.close()
        coon.close()
        return

    def readCaseFromSQL(self):
        sql = 'select id,apiurl,apimethod,apiparamvalue,apibodyvalue,apiexpectstatuscode,apiexpectresponse from apitest_apis'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        aa = cursor.execute(sql)
        info = cursor.fetchmany(aa)
        # print('info:', info)

        caselist = []
        for ii in info: # 读出来的是元组类型的字典，好在元组也有下标
            # print('ii:', ii)
            # print(type(ii))
            caselist.append(list(ii))
        coon.commit()
        cursor.close()
        coon.close()
        # 这里需要处理一下数据
        caselist = self.handleDataType(caselist)
        return caselist

    def handleDataType(self, caselist):
        for case in caselist:
            case[3] = ast.literal_eval(case[3])
            case[4] = ast.literal_eval(case[4])
            # print(type(case[3]))
            # print(type(case[4]))
            # if case[3] == '{}':
            #     case[3] = {}
            #     # pass
            # elif type(case[3]) != "None":
            #     case[3] = json.dumps(case[3])
            #     # print(case[3])
            #     case[3] = json.loads(case[3])
            #     # print(case[3])
            #     # print(type(case[3]))
            # if case[4] != 'None':
            #     case[4] = json.dumps(case[4])
            #     case[4] = json.loads(case[4])
            #     print(case[4])
            # print(type(case[3]))
            # print(type(case[4]))
        return caselist

if __name__ == '__main__':
    # Manage_sql().writeCaseToSQL(list)
    # Manage_sql().deleteCaseInSQL()
    caselist = Manage_sql().readCaseFromSQL()
    # caselist = [[29, '/2.0/user/logout', 'post', '{}', {'vendor': 'PUSH_VENDOR_UNSPECIFIED'}, 200, None],
    #             ]
    tester = Case_request()

    for case in caselist:
        print(case)
        tester.send_request(caselist)
    print('Done!')