import json
import os

import pymysql
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate, login


# Create your views here.
from django.urls import reverse

from apitest.common.case_collect_data import Case_collect
from apitest.common.manage_sql import Manage_sql, Case_request
from apitest.models import Apitest, Apistep, Apis, Headers


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
            # response = HttpResponseRedirect('apitest/home')
            # return response
            return HttpResponseRedirect(reverse('apitest/home'))
        else:
            return render(request, 'apitest/login.html', {'error': 'username or password error'})
    return render(request, 'apitest/login.html')

@login_required
def home(request):
    context = {}
    context['username'] = request.session.get('user','')
    return render(request, 'apitest/home.html', context)


def test(request):
    return render(request, 'apitest/test.html')

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
    apits_list = Apis.objects.filter(apiname__icontains=apiname)
    return render(request,"apitest/apis_manage.html",{"user":username,"apiss":apits_list})

# @login_required
# def apistepsearch(request):
#     username = request.session.get('user','')
#     apistepname = request.GET.get("apistepname","")
#     apitstep_list = Apistep.objects.filter(apiname__icontains=apistepname)
#     return render(request,"apitest/apistep_manage.html",{"user":username,"apisteps":apitstep_list})

def welcome(request):
    return render(request, "apitest/welcome.html")

def testapi(request):
    print('i test.')
    # 开始你的测试逻辑
    # 先清空数据库的数据
    Manage_sql().deleteCaseInSQL()
    # 写进新的数据，这里有个问题就是，在web更新了用例的话，这里实际上跑的还是老用例
    # 所以需要支持前端更新用例，这里每次都直接从数据库读取就好了，todo
    root = os.path.abspath('.') #获取当前工作目录路径
    filepath = os.path.join(root, 'apitest/config/swagger.json')
    print(filepath)
    case_list = Case_collect(filepath).collect_data()

    # 第四步，写进表
    Manage_sql().deleteCaseInSQL()
    Manage_sql().writeCaseToSQL(case_list)

    # 读取数据
    caselist = Manage_sql().readCaseFromSQL()

    # 进行测试
    tester = Case_request()
    caselist = tester.send_request(caselist)

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
            # 把新的数据写进表里
            case_list = Case_collect(filepath).collect_data()
            Manage_sql().deleteCaseInSQL()
            Manage_sql().writeCaseToSQL(case_list)
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
    paginator = Paginator(headers_list, 9)
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
