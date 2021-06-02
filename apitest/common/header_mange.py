# coding:utf-8
import os

import pymysql
import requests


class HeaderManage:
    @staticmethod
    def read_header(product_id):
        sql = "SELECT header_key, header_value from apitest_headers WHERE Product_id = %s"
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        param = product_id
        aa = cursor.execute(sql, param)
        info = cursor.fetchmany(aa)

        headers = []
        for ii in info:  # 读出来的是元组类型的字典
            headers.append(ii)
        headers = dict(headers)
        coon.commit()
        cursor.close()
        coon.close()
        return headers

    @staticmethod
    def update_header(product_id, host):
        url = host+'/app_auth_tokens.refresh'
        headers = HeaderManage.read_header(product_id)
        print("刷新token url:", url)
        result = requests.post(url, headers=headers, json={})
        print("刷新结果：", result.status_code)
        response_body = result.json()
        access_token = response_body['x-jike-access-token']
        refresh_token = response_body['x-jike-refresh-token']

        sql = "update apitest_headers set header_value = %s where Product_Id = %s and header_key = %s;"
        coon = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1', port=3306, charset='utf8')
        cursor = coon.cursor()
        param1 = (access_token, product_id, 'x-jike-access-token')
        param2 = (refresh_token, product_id, 'x-jike-refresh-token')
        cursor.execute(sql, param1)
        cursor.execute(sql, param2)
        coon.commit()
        cursor.close()
        coon.close()
        return
