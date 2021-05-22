# coding:utf-8
import ast
import json
import requests

import pymysql


class ManageSql:
    @staticmethod
    def write_case_to_sql(case_list):
        """
        把测试用例写进数据库
        :param case_list:
        :return:
        """
        sql = "insert into apitest_apis(api_name,api_url,api_method,api_param_value,api_body_value,api_expect_status_code,Product_id) values(%s,%s,%s,%s,%s,%s,%s);"
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()

        # 这里开始循环写入表
        for case in case_list:
            param = ('test', case[0], case[1], case[2].__str__(), case[3].__str__(), case[4].__str__(),
                     '2')  # 不转换成str会出错，因为值里面有引号
            cursor.execute(sql, param)
            coon.commit()

        cursor.close()
        coon.close()
        return

    @staticmethod
    def delete_case_in_sql():
        sql = 'delete from apitest_apis'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        cursor.execute(sql)
        coon.commit()
        cursor.close()
        coon.close()
        return

    @staticmethod
    def delete_flow_case_in_sql():
        sql = 'delete from apitest_apiflowandapis'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        cursor.execute(sql)
        coon.commit()
        cursor.close()
        coon.close()
        return

    @staticmethod
    def read_case_from_sql():
        sql = 'select id,api_url,api_method,api_param_value,api_body_value,api_expect_status_code,api_expect_response from apitest_apis'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        aa = cursor.execute(sql)
        info = cursor.fetchmany(aa)

        case_list = []
        for ii in info:  # 读出来的是元组类型的字典
            case_list.append(list(ii))
        coon.commit()
        cursor.close()
        coon.close()
        # 这里需要处理一下数据，让body和param都变回字典格式
        case_list = handle_data_type(case_list)
        return case_list

    @staticmethod
    def update_case_to_sql(case_list):
        sql = "update apitest_apis set api_response_status_code = %s,api_response = %s,api_status = %s where id = %s;"
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()

        # 这里开始循环更新表
        for case in case_list:
            param = (case[7].__str__(), case[8].__str__().strip(), case[9], case[0].__str__())  # 不转换成str会出错，因为值里面有引号
            cursor.execute(sql, param)
            coon.commit()

        cursor.close()
        coon.close()
        return

    @staticmethod
    def write_variables_to_sql(product_id, variables_dict):
        """
        把从接口里梳理出来的参数写到数据库里
        :param product_id: 对应的项目id
        :param variables_dict: 参数-值
        :return:
        """
        sql = "INSERT INTO apitest_variables(from_api,Product_id,variable_key) VALUES(%s,%s,%s)"
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        for api, variable_list in variables_dict.items():
            for variable in variable_list:
                param = (api, product_id, variable)
                cursor.execute(sql, param)
                coon.commit()
        cursor.close()
        coon.close()
        return

    @staticmethod
    def delete_variables_in_sql():
        sql = 'delete from apitest_variables'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        cursor.execute(sql)
        coon.commit()
        cursor.close()
        coon.close()
        return

    @staticmethod
    def get_variables_from_sql():
        # 把数据库里变量的值存在本地
        sql = 'select Product_id,from_api,variable_key,variable_value from apitest_variables'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        aa = cursor.execute(sql)
        info = cursor.fetchmany(aa)

        variable_list = []
        for ii in info:  # 读出来的是元组类型的字典
            variable_list.append(list(ii))
        coon.commit()
        cursor.close()
        coon.close()

        return variable_list

    @staticmethod
    def get_host_of_product(product_id):
        sql = 'select producthost from product_product where id = %s'
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        param = product_id
        aa = cursor.execute(sql, param)
        host = cursor.fetchone()[0]
        coon.commit()
        cursor.close()
        coon.close()
        return host


def handle_data_type(case_list):
    """
    将case_list里body和param从字符串变成json格式
    :param case_list:
    :return:
    """
    for case in case_list:
        case[3] = ast.literal_eval(case[3])
        case[4] = ast.literal_eval(case[4])
    return case_list
