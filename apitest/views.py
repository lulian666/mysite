import json
import os

import pymysql
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate, login


# Create your views here.
from django.urls import reverse

from apitest.common.case_collect_data import Case_collect
from apitest.common.case_readyfortest import Case_ready
from apitest.common.case_test import Case_request
from apitest.common.manage_sql import Manage_sql
from apitest.models import Apitest, Apistep, Apis, Headers, Variables
from product.models import Product


def index(request):
    return HttpResponse("Hello, world. You're at the apitest's index.")


def login(request):
    if request.POST:
        username = password = ''
        username = request.POST.get('username')  # 意思是获取html中填写的username
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            request.session['user'] = username
            return HttpResponseRedirect(reverse('apitest/home'))
        else:
            return render(request, 'apitest/login.html', {'error': 'username or password error'})
    return render(request, 'apitest/login.html')

@login_required
def home(request):
    context = {}
    context['username'] = request.session.get('user','')
    return render(request, 'apitest/home.html', context)




def logout(request):
    return render(request, 'apitest/login.html')

@login_required
def apitest_manage(request):
    apitest_list = Apitest.objects.all()
    username = request.session.get('user','')
    paginator = Paginator(apitest_list, 8)
    page = request.GET.get('page',1)
    currentPage = int(page)
    apitest_count = Apitest.objects.all().count()
    try:
        apitest_list = paginator.page(page)
    except PageNotAnInteger:
        apitest_list = paginator.page(1)
    except EmptyPage:
        apitest_list = paginator.page(paginator.num_pages)
    return render(request, "apitest/apitest_manage.html", {"user":username, "apitests": apitest_list, "apitestcounts": apitest_count})

@login_required
def apistep_manage(request):
    apistep_list = Apistep.objects.all()
    username = request.session.get('user','')
    paginator = Paginator(apistep_list, 8)
    page = request.GET.get('page',1)
    currentPage = int(page)
    apistep_count = Apistep.objects.all().count()
    try:
        apistep_list = paginator.page(page)
    except PageNotAnInteger:
        apistep_list = paginator.page(1)
    except EmptyPage:
        apistep_list = paginator.page(paginator.num_pages)
    return render(request, "apitest/apistep_manage.html", {"user":username, "apisteps": apistep_list, "apistepcounts": apistep_count})

@login_required
def apis_manage(request):
    if 'birth' in request.POST:
        # 这里要生成case了哦！
        Manage_sql().deleteCaseInSQL()
        variable_list = Manage_sql().getVariablesFromSQL()

        basic_case_list, case_list = Case_collect().collect_data()
        print(type(case_list))
        case_list = Case_ready(case_list, variable_list).data_form()
        for case in case_list:
            print('case are ready:',case)

        Manage_sql().deleteCaseInSQL()
        Manage_sql().writeCaseToSQL(case_list)

    username = request.session.get('user','')
    productList = Product.objects.all()
    apis_list = Apis.objects.all()
    paginator = Paginator(apis_list, 6)
    page = request.GET.get('page',1)
    currentPage = int(page)
    apis_count = Apis.objects.all().count()
    try:
        apis_list = paginator.page(page)
    except PageNotAnInteger:
        apis_list = paginator.page(1)
    except EmptyPage:
        apis_list = paginator.page(paginator.num_pages)
    return render(request, "apitest/apis_manage.html", {"user": username, "apiss": apis_list, "apicounts": apis_count, "products": productList})

@login_required
def test_report(request):
    username = request.session.get('user','')
    apis_list = Apis.objects.all()
    apis_count = Apis.objects.all().count()
    db = pymysql.connect(user='root', db='dj',passwd='52france',host='127.0.0.1')
    cursor = db.cursor()
    sql1 = 'SELECT count(id) FROM apitest_apis WHERE apitest_apis.apistatus=1'
    aa = cursor.execute(sql1)
    apis_pass_count = [row[0] for row in cursor.fetchmany(aa)][0]
    sql2 = 'SELECT count(id) FROM apitest_apis WHERE apitest_apis.apistatus=0'
    bb = cursor.execute(sql2)
    apis_fail_count = [row[0] for row in cursor.fetchmany(bb)][0]
    db.close()
    return render(request, "apitest/report.html", {"user":username, "apiss": apis_list, "apiscounts": apis_count, "apis_pass_count":apis_pass_count, "apis_fail_count":apis_fail_count})

def left(request):
    return render(request, "apitest/left.html")

@login_required
def search(request):
    username = request.session.get('user','')
    search_apitestname = request.GET.get("apitestname","")
    apitest_list = Apitest.objects.filter(apitestname__icontains=search_apitestname)
    # apitest_list = Apitest.objects.filter(apitestname=search_apitestname)

    return render(request,"apitest/apitest_manage.html",{"user":username,"apitests":apitest_list})

@login_required
def apissearch(request):
    username = request.session.get('user','')
    apiname = request.GET.get("apiname","")
    apis_list = Apis.objects.filter(apiname__icontains=apiname)
    return render(request,"apitest/apis_manage.html",{"user":username,"apiss":apis_list})


def welcome(request):
    return render(request, "apitest/welcome.html")

def test(request):
    productId = request.POST.get('productId')
    testResult = request.POST.get('testresult')
    # testResult = True if testResult == 1 else False
    print(productId)
    print(testResult)
    productList = Product.objects.all()
    print(productList)

    selectedProduct = "可不选"

    selector = {"-1": "可不选",
                "0": "测试不通过",
                "1": "测试通过"}
    selectedTestResult = selector.get(testResult)
    # testResultValue = selector.
    apisList = Apis.objects.all()
    if productId != '-1':
        apisList = apisList.filter(Product_id=productId)
        selectedProduct = productList.get(id=productId)
    if testResult == '-1':
        apisList = apisList.filter(apistatus__isnull=True)
        print('x')
    else:
        apisList = apisList.filter(apistatus=True if testResult == '1' else False)
        # selectedTestResult = "测试不通过" if testResult == "0" else "测试通过"
        print('y')
    # print(len(apisList))
    return render(request, 'apitest/apis_manage.html', {'apiss': apisList, "products": productList, "selectedProduct": selectedProduct, "selectedTestResult": selectedTestResult, "selector": selector})

def testapi(request):
    print('i test.')
    # 开始你的测试逻辑

    # 读取数据（根据给出的条件）
    caselist = Manage_sql().readCaseFromSQL()

    # 获取host
    host = Manage_sql().getHostofProduct(2)

    # 进行测试
    tester = Case_request()
    caselist = tester.send_request(caselist, host)

    Manage_sql().updateCaseToSQL(caselist)
    print('Done!')

    username = request.session.get('user','')
    apis_list = Apis.objects.all()
    paginator = Paginator(apis_list, 8)
    page = request.GET.get('page',1)
    currentPage = int(page)
    apis_count = Apis.objects.all().count()
    try:
        apis_list = paginator.page(page)
    except PageNotAnInteger:
        apis_list = paginator.page(1)
    except EmptyPage:
        apis_list = paginator.page(paginator.num_pages)
    return render(request, "apitest/apis_manage.html", {"user": username, "apiss": apis_list,"apicounts": apis_count})

# 处理源数据
def datasource(request):
    source = request.POST.get('source','').strip()
    error = ''
    # 区分两个按钮
    if 'analysis' in request.POST:
        if not check_json_format(source):
            error = 'not a legal json'
        else:
            error = 'this is a legal json'
    elif 'save' in request.POST:
        root = os.path.abspath('.') #获取当前工作目录路径
        if not check_json_format(source):
            error = 'not a legal json'
        elif source != "{}":
            error = 'this is a legal json'
            filepath = os.path.join(root, 'apitest/config/temp.json')
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(source))
            f.close()
            # 把接口里的变量保存下来
            basic_case_list, case_list = Case_collect().collect_data()
            variables_dict = {}
            for case in basic_case_list:
                print('basic case:',case)  # 这个是还没有替换值的case
                if case[3] != {}: #处理body的
                    param_list = []
                    for num, keys in list(enumerate(case[3])):
                        if 'enum' not in case[3][keys]:
                            # 如果这个参数的值里面，有enum这个字段，就不需要存了
                            param_list.append(keys)
                    if len(param_list) >= 0:
                        print("param_list:", param_list)
                        variables_dict.update({case[0]:param_list})
                elif case[2] != {}:
                    #处理parameters的
                    param_list = []
                    for num, keys in list(enumerate(case[2])):
                        if 'enum' not in case[2][keys]:
                            # 如果这个参数的值里面，有enum这个字段，就不需要存了
                            param_list.append(keys)
                    if len(param_list) >= 0:
                        print("param_list:", param_list)
                        variables_dict.update({case[0]:param_list})
            Manage_sql().deleteVariablesInSQL()
            Manage_sql().writeVariablesToSQL(2, variables_dict)
            # Manage_sql().deleteCaseInSQL()
            # Manage_sql().writeCaseToSQL(case_list)
        else:
            error = 'this is empty!!'

    username = request.session.get('user','')
    apis_list = Apis.objects.all()
    paginator = Paginator(apis_list, 8)
    page = request.GET.get('page', 1)
    currentPage = int(page)
    apis_count = Apis.objects.all().count()
    try:
        apis_list = paginator.page(page)
    except PageNotAnInteger:
        apis_list = paginator.page(1)
    except EmptyPage:
        apis_list = paginator.page(paginator.num_pages)
    # print("source:", source)
    return render(request, "apitest/datasource_manage.html", {'error': error, 'data': source, "user": username, "apiss": apis_list,"apicounts": apis_count})

# header 管理
def api_header(request):
    username = request.session.get('user','')
    headers_list = Headers.objects.all()
    paginator = Paginator(headers_list, 12)
    page = request.GET.get('page', 1)
    currentPage = int(page)
    headers_count = Headers.objects.all().count()
    try:
        headers_list = paginator.page(page)
    except PageNotAnInteger:
        headers_list = paginator.page(1)
    except EmptyPage:
        headers_list = paginator.page(paginator.num_pages)
    return render(request, "apitest/api_header.html", {"user": username, "headers": headers_list, "apicounts": headers_count})

# 变量管理
def variables_manage(request):
    username = request.session.get('user','')
    variables_list = Variables.objects.all()
    paginator = Paginator(variables_list, 12)
    page = request.GET.get('page', 1)
    currentPage = int(page)
    variables_count = Variables.objects.all().count()
    try:
        variables_list = paginator.page(page)
    except PageNotAnInteger:
        variables_list = paginator.page(1)
    except EmptyPage:
        variables_list = paginator.page(paginator.num_pages)

    return render(request, "apitest/variables_manage.html", {"user": username, "variables": variables_list, "variablecounts": variables_count, "warning": "只点击一次就好，会跳转到用例列表"})

def check_json_format(raw_msg):
    """
    用于判断一个字符串是否符合Json格式
    :param self:
    :return:
    """
    if isinstance(raw_msg, str) and not raw_msg.isdigit():
        raw_msg.strip()
        try:
          json.loads(raw_msg)
        except ValueError:
            return False
        return True
    else:
        return False
