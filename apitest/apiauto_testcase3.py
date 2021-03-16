# -*- coding:utf-8 -*-
import requests, time, sys, re
import urllib, zlib
import pymysql
from trace import CoverageResults
import json
from idlelib.rpc import response_queue
from time import sleep

HOSTNAME = '127.0.0.1'


def readSQLcase():
    sql = "SELECT id, apiname, apiurl, apimethod, apiparamvalue, apiresult, apistatus from apitest_apistep where apitest_apistep.Apitest_id=1 "
    coon = pymysql.connect(user='root', db='dj',passwd='52france',host='127.0.0.1',port=3306,charset='utf8')
    cursor = coon.cursor()
    aa = cursor.execute(sql)
    info = cursor.fetchmany(aa)
    for ii in info:
        case_list = []
        case_list.append(ii)
        interfaceTest(case_list)
    coon.commit()
    cursor.close()
    coon.close()

def interfaceTest(case_list):
    res_flags = []
    request_urls = []
    responses = []
    strinfo = re.compile('{TaskID}')
    strinfo1 = re.compile('{AssetID}')
    strinfo2 = re.compile('{PointID}')
    assetinfo = re.compile('{assetno}')
    tasknoifo = re.compile('{taskno}')
    schemainfo = re.compile('{schema}')

    for case in case_list:
        try:
            case_id = case[0]
            # print("case_id: " + case_id)
            interface_name = case[1]
            method = case[3]
            url = case[2]
            param = case[4] #apiparamvalue
            res_check = case[5]
        except Exception as e:
            return '测试用例格式不争气%s' %e

        # new_url = 'http://' + url
        if param == '':
            new_url = 'http://' + 'api.test.com.cn' + url
        elif param == 'null':
            new_url = 'http://' + url
        else:
            url =  strinfo.sub(TaskId, url)
            param = strinfo.sub(TaskId,param)
            param = tasknoifo.sub(taskno,param)
            new_url = 'http://' + 'api.test.com.cn' + url
            request_urls.append(new_url)

        if method.upper() == 'GET':
            headers = {'Authorization':'', 'Content-Type':'application/json'}
            if "=" in urlParam(param):
                data = None
                print(str(case_id) + 'request is get' + new_url.encode('utf-8') + '?' + urlParam(param).encode('utf-8'))
                results = requests.get(new_url + '?' + urlParam(param), data, headers=headers).text
                print('response is get ' + results.encode('utf-8'))
                responses.append(results)
                res = readRes(results,'')
            else:
                print('request is get ' + new_url + '\nbody is ' + urlParam(param))
                data = None
                req = urllib.request.Request(url = new_url, data = data, headers = headers, method = "GET")
                results = urllib.request.urlopen(req).read()
                print("results:" + results)
                print('resonse is get ')
                print(results)
                res = readRes(results, res_check)

            if 'pass' == res:
                writeResult(case_id,'1')
                res_flags.append('pass')
            else:
                res_flags.append('fail')
                writeResult(case_id,'0')

        if method.upper() == 'PUT':
            headers = {'Host':HOSTNAME, 'Connection':'keep-alive', 'CredentialId':id, 'Content-Type':'application/json'}
            body_data = param
            results = requests.put(url=url, data=body_data,headers=headers)
            responses.append(results)
            res = readRes(results, res_check)
            if 'pass' == res:
                writeResult(case_id,'pass')
                res_flags.append('pass')
            else:
                res_flags.append('fail')
                writeResult(case_id,'fail')
                writeBug(case_id,interface_name,new_url,results,res_check)

            try:
                preOrderSN(results)
            except:
                print('ok')

        if method.upper() == 'PATCH':
            headers =  {'Authorization':'Credential '+ id, 'Content-Type':'application/json'}
            data = None
            results = requests.patch(new_url + '?' + urlParam(param), data, headers=headers).text
            responses.append(results)
            res = readRes(results, res_check)
            if 'pass' == res:
                writeResult(case_id,'pass')
                res_flags.append('pass')
            else:
                res_flags.append('fail')
                writeResult(case_id,'fail')
                writeBug(case_id,interface_name,new_url,results,res_check)
            try:
                preOrderSN(results)
            except:
                print('ok')

        if method.upper() == 'POST':
            headers =  {'Authorization':'Credential '+ id, 'Content-Type':'application/json'}
            if "=" in urlParam(param):
                data = None
                results = requests.post(new_url + '?' + urlParam(param), data, headers=headers).text
                print('response is post ' + results.encode('utf-8'))
                responses.append(results)
                res = readRes(results, '')
            else:
                print(str(case_id) + ' request is ' + new_url.encode('utf-8') + ' body is ' + urlParam(param).encode('utf-8'))
                results = requests.post(new_url,data = urlParam(param).encode('utf-8'), headers=headers).text
                print(' response is post ' + results.encode('utf-8'))
                responses.append(results)
                res = readRes(results, res_check)
            if 'pass' == res:
                writeResult(case_id,'1')
                res_flags.append('pass')
            else:
                res_flags.append('fail')
                writeResult(case_id,'0')
                writeBug(case_id,interface_name,new_url,results,res_check)
            try:
                TaskId(results)
            except:
                print('ok')

def readRes(res, res_check):
    res = res.decode().replace('":"',"=").replace('":',"=")
    res_check = res_check.split(';')
    for s in res_check:
        if s in res:
            pass
        else:
            return '错误，返回参数和预期结果不一致' + s
    return 'pass'

def urlParam(param):
    param1 = param.replace('&quot;','"')
    return param1

def CredentualId():
    global id
    url = 'http://' + 'api.test.com.cn' + '/api/Security/Authentication/Signin/web'
    body_data = json.dump({"Identity":'test', "Password":'test'})
    headers = {'Connection':'keep-alive', 'Content-Type':'application/json'}
    response = requests.post(url=url, data=body_data, headers=headers)
    data = response.text
    regx = '.*"CredentialId":"(.*)","Scene"'
    pm = re.search(regx, data)
    id = pm.group(1)

def preOrderSN(results):
    global preOrderSN
    regx = '.*"preOrderSN":"(.*)","toHome"'
    pm = re.search(regx, results)
    if pm:
        preOrderSN = pm.group(1).encode('utf-8')
        return preOrderSN
    return False

def TaskId(results):
    global TaskId
    regx = '.*"TaskId":"(.*)","PlanId"'
    pm = re.search(regx, results)
    if pm:
        TaskId = pm.group(1).encode('utf-8')
        return TaskId
    return False

def taskno(results):
    global taskno
    a = int(time.time())
    taskno = 'task_' + str(a)
    return taskno

def writeResult(case_id, result):
    result = result.encode('utf-8')
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    sql = "UPDATE apitest_apistep set apitest_apistep.apistatus=%s where apitest_apistep.Apitest_id=%s;"
    param = (result, case_id)
    print('api autotest result is ' + result.decode())
    coon = pymysql.connect(user='root', db='dj',passwd='52france',host='127.0.0.1',port=3306,charset='utf8')
    cursor = coon.cursor()
    cursor.execute(sql,param)
    coon.commit()
    cursor.close()
    coon.close()

def writeBug(bug_id, interface_name, request, response, res_check):
    interface_name = interface_name.encode('utf-8')
    res_check = res_check.encode('utf-8')
    request = request.encode('utf-8')
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    bugname = str(bug_id) + '_' + interface_name.decode() + '_出错了'
    bugdetail = '【请求数据】<br />' + request.decode() + '<br/>' + '【预期结果】<br/>' + res_check.decode() + '<br/>' + '<br/>' + '【响应数据】<br/>' + '<br/>' + response.decode()
    print(bugdetail)
    sql = "INSERT INTO 'bug_bug'("\
          "bugname,bugdetail,bugstatus,buglevel,bugcreater,bugassign,create_time,Product_id)"\
          "VALUES('%s','%s','1','1','dj','dj','%s','2');"%(bugname,pymysql.escape_string(bugdetail),now)
    coon = pymysql.connect(user='root', db='dj',passwd='52france',host='127.0.0.1',port=3306,charset='utf8')
    cursor = coon.cursor()
    cursor.execute(sql)
    coon.commit()
    cursor.close()
    coon.close()

if __name__ == '__main__':
    readSQLcase()
    print('Done!')
    time.sleep(1)