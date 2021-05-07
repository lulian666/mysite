# coding:utf-8
import ast
import json
import requests

import pymysql

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

        caselist = []
        for ii in info: # 读出来的是元组类型的字典
            caselist.append(list(ii))
        coon.commit()
        cursor.close()
        coon.close()
        # 这里需要处理一下数据，让body和param都变回字典格式
        caselist = self.handleDataType(caselist)
        return caselist

    def handleDataType(self, caselist):
        for case in caselist:
            case[3] = ast.literal_eval(case[3])
            case[4] = ast.literal_eval(case[4])
        return caselist

    def updateCaseToSQL(self, caselist):
        sql = "update apitest_apis set apiresponsestatuscode = %s,apiresponse = %s,apistatus = %s where id = %s;"
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()

        # 这里开始循环更新表
        for case in caselist:
            print(case)
            param = (case[7].__str__(), case[8].__str__().strip(), case[9], case[0].__str__()) #不转换成str会出错，因为值里面有引号
            cursor.execute(sql, param)
            coon.commit()

        cursor.close()
        coon.close()
        return

    def writeVariablesToSQL(self, productId, variables_dict):
        sql = "INSERT INTO apitest_variables(from_api,Product_id,variable_key) VALUES(%s,%s,%s)"
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        for api, variable_list in variables_dict.items():
            print(api,variable_list)
            for variable in variable_list:
                param = (api, productId, variable)
                cursor.execute(sql, param)
                coon.commit()
        cursor.close()
        coon.close()
        return

    def deleteVariablesInSQL(self):
        sql = 'delete from apitest_variables'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        cursor.execute(sql)
        coon.commit()
        cursor.close()
        coon.close()
        return

    def getVariablesFromSQL(self):
        # 把数据库里变量的值存在本地
        sql = 'select Product_id,from_api,variable_key,variable_value from apitest_variables'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        aa = cursor.execute(sql)
        info = cursor.fetchmany(aa)

        variable_list = []
        for ii in info: # 读出来的是元组类型的字典
            variable_list.append(list(ii))
        coon.commit()
        cursor.close()
        coon.close()

        return variable_list

    def getHostofProduct(self, productId):
        sql = 'select producthost from product_product where id = %s'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        param = (productId)
        aa = cursor.execute(sql, param)
        host = cursor.fetchone()[0]
        print(host, type(host))
        coon.commit()
        cursor.close()
        coon.close()
        return host

# if __name__ == '__main__':
    # Manage_sql().writeCaseToSQL(list)
    # Manage_sql().deleteCaseInSQL()
    # caselist = Manage_sql().readCaseFromSQL()
    # caselist = [[334, '/2.0/user/logout', 'post', '{}', {'vendor': 'PUSH_VENDOR_UNSPECIFIED'}, 200, None, 200, 1234],]
    # tester = Case_request()

    # for case in caselist:
    #     print(case)
    # tester.send_request(caselist)
    # print('Done!')