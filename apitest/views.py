import ast
import json
import os

import pymysql
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from apitest.common.case_collect_data import CaseCollect
from apitest.common.case_readyfortest import CaseReady
from apitest.common.case_test import TestCaseRequest
from apitest.common.managesql import ManageSql
from apitest.models import ApiFlowTest, Apis, Headers, Variables
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
    context = {'username': request.session.get('user', '')}
    return render(request, 'apitest/home.html', context)


def logout(request):
    return render(request, 'apitest/login.html')


@login_required
def api_flow_test_manage(request):
    username = request.user
    api_flow_test_list = ApiFlowTest.objects.all()
    api_flow_test_counts, api_flow_test_page_list = paginator(request, api_flow_test_list, 6)
    return render(request, "apitest/api_flow_test_manage.html",
                  {"username": username, "api_flow_test_list": api_flow_test_page_list, "api_flow_test_counts": api_flow_test_counts})


@login_required
@csrf_exempt
def form_api_flow_case(request):
    username = request.user
    api_for_test_list = Apis.objects.filter(api_expect_status_code=200).filter(Product_id=2)
    # api_for_test_list = api_for_test_list.values('api_url').distinct()
    # print(api_for_test_list.count())
    # print(api_for_test_list.all())
    return render(request, "apitest/form_api_flow_case.html",
                  {"username": username,
                   'api_for_test_list': api_for_test_list})


@login_required
def apis_manage(request):
    """
    单一接口页面管理
    :param request:
    :return:
    """
    product_list = Product.objects.all()
    api_list = Apis.objects.all()
    test_result_list = [0, 1]  # {"0": "测试不通过","1": "测试通过"}
    selected_test_result = selected_product_id = -1  # 默认是-1 表示全选

    if 'selected_test_result' in request.GET:
        api_list, selected_test_result, selected_product_id = list_filter(request.GET, api_list)

    if request.method == 'POST':
        api_list, selected_test_result, selected_product_id = list_filter(request.POST, api_list)
        if 'run_test' in request.POST:
            test_case(api_list)

    apis_count, apis_page_list = paginator(request, api_list, 6)
    username = request.user
    return render(request, 'apitest/apis_manage.html',
                  {'api_list': apis_page_list, "product_list": product_list, 'username': username,
                   'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                   'selected_product_id': selected_product_id, 'apis_count': apis_count})


def save_case_locally(case_list, host):
    pass


def test_case(model_list):
    """
    根据筛选出来的list来执行测试
    :param model_list: QuerySet类型
    :return:
    """
    case_list = []

    for case in model_list:
        case_list.append([case.id, case.apiurl, case.apimethod, ast.literal_eval(case.apiparamvalue), ast.literal_eval(case.apibodyvalue),
                         case.apiexpectstatuscode, case.apiexpectresponse])

    # 获取host
    host = ManageSql().get_host_of_product(2)
    # todo: 这里的一个问题就是，我的机制是默认所有case都隶属同一个项目，所以host都一样，但实际情况还是要每一条case有自己的host

    # 进行测试
    tester = TestCaseRequest(case_list, host)
    case_list = tester.send_request()

    # 用pytest进行测试
    # save_case_locally(case_list, host)
    #
    # root = os.path.abspath('.')
    # file = os.path.join(root, 'apitest')
    # cmd = 'py.test -s -v %s' % file
    # os.system(cmd)

    # 将测试结果更新数据库
    ManageSql.update_case_to_sql(case_list)


@login_required
def test_report(request):
    username = request.session.get('user', '')
    apis_list = Apis.objects.all()
    apis_count = Apis.objects.all().count()
    db = pymysql.connect(user='root', db='dj', passwd='52france', host='127.0.0.1')
    cursor = db.cursor()
    sql1 = 'SELECT count(id) FROM apitest_apis WHERE apitest_apis.apistatus=1'
    aa = cursor.execute(sql1)
    apis_pass_count = [row[0] for row in cursor.fetchmany(aa)][0]
    sql2 = 'SELECT count(id) FROM apitest_apis WHERE apitest_apis.apistatus=0'
    bb = cursor.execute(sql2)
    apis_fail_count = [row[0] for row in cursor.fetchmany(bb)][0]
    db.close()
    return render(request, "apitest/report.html",
                  {"user": username, "apis_list": apis_list, "apis_count": apis_count, "apis_pass_count": apis_pass_count,
                   "apis_fail_count": apis_fail_count})


def left(request):
    return render(request, "apitest/left.html")


@login_required
def search(request):
    username = request.session.get('user', '')
    search_apitestname = request.GET.get("apitestname", "")
    apitest_list = ApiFlowTest.objects.filter(apitestname__icontains=search_apitestname)
    return render(request, "apitest/api_flow_test_manage.html", {"user": username, "apitests": apitest_list})


@login_required
def apissearch(request):
    username = request.session.get('user', '')
    apiname = request.GET.get("apiname", "")
    apis_list = Apis.objects.filter(apiname__icontains=apiname)
    return render(request, "apitest/apis_manage.html", {"user": username, "apiss": apis_list})


def welcome(request):
    return render(request, "apitest/welcome.html")


# 处理源数据
def datasource(request):
    source = request.POST.get('source', '').strip()
    error = ''
    if 'analysis' in request.POST:
        if not check_json_format(source):
            error = 'not a legal json'
        else:
            error = 'this is a legal json'
    elif 'save' in request.POST:
        root = os.path.abspath('.')  # 获取当前工作目录路径
        if not check_json_format(source):
            error = 'not a legal json'
        elif source != "{}":
            error = 'this is a legal json'
            filepath = os.path.join(root, 'apitest/config/temp.json')
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(source))
            f.close()
            # 把接口里的变量保存下来
            save_variables_to_sql()
        else:
            error = 'this is empty!!'

    username = request.user
    apis_list = Apis.objects.all()
    apis_count, apis_page_list = paginator(request, apis_list, 8)
    return render(request, "apitest/datasource_manage.html",
                  {'error': error, 'data': source, "username": username, "apis_list": apis_page_list, "apis_count": apis_count})


# header 管理
def api_header(request):
    username = request.user
    headers_list = Headers.objects.all()
    headers_count, headers_page_list = paginator(request, headers_list, 6)
    return render(request, "apitest/api_header.html",
                  {"username": username, "headers": headers_page_list, "apicounts": headers_count})


# 变量管理
def variables_manage(request):
    if 'birth' in request.POST:
        # 这里要生成case了哦！
        ManageSql.delete_flow_case_in_sql()
        ManageSql.delete_case_in_sql()
        variable_list = ManageSql.get_variables_from_sql()
        basic_case_list, case_list = CaseCollect().collect_data()
        case_list = CaseReady(case_list, variable_list).data_form()
        ManageSql.write_case_to_sql(case_list)

        # 跳转去单一接口列表页
        product_list = Product.objects.all()
        api_list = Apis.objects.all()
        test_result_list = [0, 1]  # {"0": "测试不通过","1": "测试通过"}
        selected_test_result = selected_product_id = -1  # 默认是-1 表示全选
        apis_count, apis_page_list = paginator(request, api_list, 6)
        return render(request, 'apitest/apis_manage.html',
                      {'api_list': apis_page_list, "product_list": product_list,
                       'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                       'selected_product_id': selected_product_id, 'apis_count': apis_count})

    username = request.user
    variables_list = Variables.objects.all()
    variables_count, variables_page_list = paginator(request, variables_list, 6)
    return render(request, "apitest/variables_manage.html",
                  {"username": username, "variables": variables_page_list, "variablecounts": variables_count,
                   "warning": "只点击一次就好，会跳转到用例列表"})


def save_variables_to_sql():
    """
    将temp.json中接口用到的变量都存到数据库里
    :return:
    """
    basic_case_list, case_list = CaseCollect().collect_data()
    variables_dict = {}
    for case in basic_case_list:
        if case[3] != {}:  # 处理body的
            variables_dict = search_variables(case[3], case[0], variables_dict)
        elif case[2] != {}:
            variables_dict = search_variables(case[2], case[0], variables_dict)
    ManageSql().delete_variables_in_sql()
    ManageSql().write_variables_to_sql(2, variables_dict)


def search_variables(case_variables, case_name, variables_dict):
    """
    找出传入的case_variables中有多少个变量
    :param case_variables: 一般传入的是body或者parameters
    :param case_name: 一般是接口url，用作接口名称
    :param variables_dict: 
    :return: 
    """
    param_list = []
    for num, keys in list(enumerate(case_variables)):
        if 'enum' not in case_variables[keys]:
            # 如果这个参数的值里面，有enum这个字段，就不需要存了
            param_list.append(keys)
    if len(param_list) >= 0:
        variables_dict.update({case_name: param_list})
    return variables_dict


def check_json_format(raw_msg):
    """
    用于判断一个字符串是否符合Json格式
    :param raw_msg:
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


def paginator(request, page_list, number):
    """
    分页函数
    :param request:
    :param model:
    :param page_list: 需要分页的list
    :param number: 一页分多少
    :return: 列表的总数和对应页数的list
    """
    page_list = page_list.order_by('id')
    paginator = Paginator(page_list, number)
    page = request.GET.get('page', 1)
    list_count = page_list.__len__()

    try:
        page_list = paginator.page(page)
    except PageNotAnInteger:
        page_list = paginator.page(1)
    except EmptyPage:
        page_list = paginator.page(paginator.num_pages)

    return list_count, page_list


def list_filter(request, list_to_filter):
    """
    根据项目id和测试结果来过滤用例列表
    :param request:
    :param list_to_filter:
    :return:
    """
    selected_product_id = request.get('selected_product_id')
    selected_test_result = request.get('selected_test_result')
    list_filtered = list_to_filter

    if selected_product_id != '-1':
        list_filtered = list_to_filter.filter(Product_id=selected_product_id)
    if selected_test_result != '-1':
        list_filtered = list_to_filter.filter(api_status=True if selected_test_result == '1' else False)

    return list_filtered, int(selected_test_result), int(selected_product_id)