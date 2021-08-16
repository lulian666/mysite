# coding:utf-8
import ast
import json

import pymysql
from django.utils.datetime_safe import datetime

import mysite.settings
from apitest.models import Variables, Apis


class ManageSql:
    user = mysite.settings.DATABASES['default']['USER']
    db = mysite.settings.DATABASES['default']['NAME']
    passwd = mysite.settings.DATABASES['default']['PASSWORD']
    host = mysite.settings.DATABASES['default']['HOST']
    port = int(mysite.settings.DATABASES['default']['PORT'])

    @staticmethod
    def write_case_to_sql(case_list, product_id):
        """
        把测试用例写进数据库，插入的原则，如果和已有的接口url一样，参数的数量和名字一样，参数的值也都一样，就不插入
        :param product_id:
        :param case_list:
        :return:
        """
        cases = Apis.objects.filter(Product_id=product_id)
        sql = "insert into apitest_apis(api_name,api_url,api_method,api_param_value,api_body_value,api_expect_status_code,Product_id) values(%s,%s,%s,%s,%s,%s,%s);"
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
        cursor = coon.cursor()
        # 这里开始循环写入表
        # url、parameter、body都一样
        # 如果本身没有case，那直接添加就好了
        if len(cases) == 0:
            for case in case_list:
                param = (case[0], case[1], case[2], case[3].__str__(), case[4].__str__(), case[5].__str__(),
                         product_id)
                cursor.execute(sql, param)
                coon.commit()
        else:
            for case in case_list:
                # 先判断url是不是在已有的url池里，不在就是新接口
                if case[1] not in list(cases.values_list("api_url", flat=True)):
                    param = (case[0], case[1], case[2], case[3].__str__(), case[4].__str__(), case[5].__str__(),
                             product_id)
                    cursor.execute(sql, param)
                    coon.commit()
                else:
                    remain_cases = cases.filter(api_url=case[1])
                    case_in = False
                    for case_in_sql in remain_cases:
                        # 下面两个是待写入接口里body和params的长度
                        variable_count_in_parameter = len(case[3])
                        variable_count_in_body = len(case[4])
                        n_for_parameter = n_for_body = 0
                        # 下面两个是数据库接口里body和params
                        body = ast.literal_eval(case_in_sql.api_body_value)
                        parameter = ast.literal_eval(case_in_sql.api_param_value)
                        # 统计body和params里面各有多少个参数
                        variable_count_in_sql_case_parameter = len(parameter)
                        variable_count_in_sql_case_body = len(body)
                        # 挨个分析待写入接口里的参数
                        for variable, variable_value in case[3].items():
                            if variable in parameter:
                                n_for_parameter += 1
                                # if variable_value == parameter[variable]:  # 这里的条件除了参数名字要一样，值也得一样，是否过于苛刻？
                                #     n_for_parameter += 1
                        for variable, variable_value in case[4].items():
                            if variable in body:
                                n_for_body += 1
                                # if variable_value == body[variable]:
                                #     n_for_body += 1
                        # 如果待写入接口的body和param的每一个参数，都在数据库接口里面，且数量刚好相等，且n_for_parameter、 n_for_body不都为0
                        if variable_count_in_parameter == n_for_parameter and variable_count_in_body == n_for_body and variable_count_in_sql_case_body == variable_count_in_body and variable_count_in_sql_case_parameter == variable_count_in_parameter:
                            case_in = True
                        if n_for_parameter == 0 and n_for_body == 0:
                            case_in = True
                    if not case_in:
                        print('写入了case：', case)
                        param = (case[0], case[1], case[2], case[3].__str__(), case[4].__str__(), case[5].__str__(),
                                 product_id)
                        cursor.execute(sql, param)
                        coon.commit()
        cursor.close()
        coon.close()
        return

    @staticmethod
    def update_variable_in_case(product_id):
        variable_list = Variables.objects.filter(Product_id=product_id)
        case_list = Apis.objects.filter(Product_id=product_id)
        for api in case_list:
            body = ast.literal_eval(api.api_body_value)
            parameter = ast.literal_eval(api.api_param_value)
            # 把body和parameter里面的变量值都替换掉，然后再把api更新一下
            body = update(variable_list, body, api.api_url)
            api.api_body_value = body

            parameter = update(variable_list, parameter, api.api_url)
            api.api_param_value = parameter
            api.save()
        return

    @staticmethod
    def read_case_from_sql():
        sql = 'select id,api_url,api_method,api_param_value,api_body_value,api_expect_status_code,api_expect_response from apitest_apis'
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
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
        sql = "update apitest_apis set api_response_status_code = %s,api_response = %s,test_result = %s,api_response_last_time = %s where id = %s;"
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
        cursor = coon.cursor()

        # 这里开始循环更新表
        for case in case_list:
            param = (case[8].__str__(), case[9].__str__().strip(), case[10], json.dumps(case[7]), case[0].__str__())  # 不转换成str会出错，因为值里面有引号
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
        variables = Variables.objects.filter(Product_id=product_id)
        sql1 = "INSERT INTO apitest_variables(from_api,Product_id,variable_key,variable_optional,variable_type) VALUES(%s,%s,%s,%s,%s)"
        sql2 = "update apitest_variables set variable_optional = %s,variable_type = %s where from_api = %s and variable_key = %s and Product_id = %s;"
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
        cursor = coon.cursor()
        for api, variable_list in variables_dict.items():
            for variable_info in variable_list:
                if api not in variables.values_list('from_api', flat=True):
                    param = (api, product_id, variable_info['variable_key'], variable_info['variable_optional'],
                             variable_info['variable_type'])
                    cursor.execute(sql1, param)
                    coon.commit()
                # 这里有个小bug，如果变量只是更改了属性，比如variable_optional或者variable_type，原本的判断方式，可能会不去更新
                # 更新成，如果变量名一样，属性不一样时，更新属性
                elif variable_info['variable_key'] not in variables.filter(from_api=api).values_list("variable_key",
                                                                                                     flat=True):
                    param = (api, product_id, variable_info['variable_key'], variable_info['variable_optional'],
                             variable_info['variable_type'])
                    cursor.execute(sql1, param)
                    coon.commit()
                elif variable_info['variable_optional'] != variables.filter(from_api=api).filter(variable_key=variable_info['variable_key']).values_list("variable_optional", flat=True) or variable_info['variable_type'] != variables.filter(from_api=api).filter(variable_key=variable_info['variable_key']).values_list("variable_type", flat=True):
                    param = (variable_info['variable_optional'], variable_info['variable_type'], api, variable_info['variable_key'], product_id)
                    cursor.execute(sql2, param)
                    coon.commit()
        cursor.close()
        coon.close()
        return

    @staticmethod
    def get_variables_from_sql(selected_product_id):
        # 把数据库里变量的值存在本地
        sql = 'select Product_id,from_api,variable_key,variable_value from apitest_variables where Product_id = %s'
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
        param = selected_product_id
        cursor = coon.cursor()
        aa = cursor.execute(sql, param)
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
        sql = 'select product_host from product_product where id = %s'
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
        cursor = coon.cursor()
        param = product_id
        aa = cursor.execute(sql, param)
        host = cursor.fetchone()[0]
        coon.commit()
        cursor.close()
        coon.close()
        return host

    @staticmethod
    def write_flow_case_to_sql(case_name, case_desc, case_tester, product_id):
        sql = "insert into apitest_apiflowtest(case_name,case_desc,case_tester,Product_id) values(%s,%s,%s,%s);"
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
        cursor = coon.cursor()
        param = (case_name, case_desc, case_tester, product_id)  # 不转换成str会出错，因为值里面有引号
        cursor.execute(sql, param)
        coon.commit()

        sql2 = "select id from apitest_apiflowtest where case_name = %s;"
        param2 = case_name
        aa = cursor.execute(sql2, param2)
        case_id = cursor.fetchone()[0]
        coon.commit()

        cursor.close()
        coon.close()
        return case_id

    @staticmethod
    def write_to_table_api_flow_and_apis(flow_case_id, id_list, io_list):
        create_time = datetime.now()
        sql = "insert into apitest_apiflowandapis(ApiFlowTest_id,Apis_id,output_parameter,input_parameter,execution_order,create_time) values(%s,%s,%s,%s,%s,%s);"
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
        cursor = coon.cursor()
        # execution_order应该就是传入list的顺序
        execution_order = 0
        for index, api_id in enumerate(id_list):
            if api_id != "":
                execution_order = execution_order + 1
                param = (flow_case_id, api_id[0], io_list[index][0], io_list[index][1], execution_order, create_time)
                # param = (flow_case_id, api_id, output_parameter, input_parameter, execution_order)  # 不转换成str会出错，因为值里面有引号
                cursor.execute(sql, param)
                coon.commit()

        cursor.close()
        coon.close()

    @staticmethod
    def is_value_only(value, column_name, table_name):
        value_list = ManageSql.get_one_column_value(column_name, table_name)
        return not (value in value_list)

    @staticmethod
    def get_one_column_value(column_name, table_name):
        sql = "select %s from %s;" % (column_name, table_name)
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
        cursor = coon.cursor()

        aa = cursor.execute(sql)
        info = cursor.fetchmany(aa)

        value_list = []
        for ii in info:  # 读出来的是元组类型的字典
            value_list.append(ii[0])
        coon.commit()

        cursor.close()
        coon.close()
        return value_list

    @staticmethod
    def add_new_product(new_product_name, new_product_description, new_product_host):
        create_time = datetime.now()
        sql = "insert into product_product(product_name,product_desc,product_host,create_time) values(%s,%s,%s,%s);"
        coon = pymysql.connect(user=ManageSql.user, db=ManageSql.db, passwd=ManageSql.passwd, host=ManageSql.host, port=ManageSql.port, charset='utf8')
        cursor = coon.cursor()
        param = (new_product_name, new_product_description, new_product_host, create_time)  # 不转换成str会出错，因为值里面有引号
        cursor.execute(sql, param)
        coon.commit()

    @staticmethod
    def write_header_to_sql(header_key, header_value, product_id):
        # 这里还要考虑会不会重复（可能不用，只有本来无header的是才会用到这里）
        sql = "insert into apitest_headers(header_key,header_value,product_id) values(%s,%s,%s);"
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        param = (header_key, header_value, product_id)  # 不转换成str会出错，因为值里面有引号
        cursor.execute(sql, param)
        coon.commit()


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


def update(variable_list, body, url):
    for key, value in body.items():
        if isinstance(value, dict):
            for value_key, value_value in value.items():
                try:
                    answer = variable_list.filter(from_api=url).filter(variable_key=value_key).values_list(
                        "variable_value", flat=True)[0]
                except:
                    answer = None
                if value_value is None or value_value == "None":  # enum的不需要代替
                    body[key][value_key] = answer
                elif answer is not None and answer != "None" and answer != value:
                    body[key][value_key] = answer
        else:
            try:
                answer = variable_list.filter(from_api=url).filter(variable_key=key).values_list(
                    "variable_value", flat=True)[0]
            except:
                answer = None
            if value is None or value == "None":  # enum的不需要代替
                body[key] = answer
            elif answer is not None and answer != "None" and answer != value:
                body[key] = answer
    return body
