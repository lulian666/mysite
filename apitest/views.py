import ast
import json
import os
from os import listdir

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
from apitest.models import ApiFlowTest, Apis, Headers, Variables, ApiFlowAndApis
from product.models import Product


def login(request):
    if request.POST:
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
@csrf_exempt
def form_api_flow_case(request):
    username = request.user
    api_to_choose_list = Apis.objects.filter(api_expect_status_code=200).filter(Product_id=2)
    case_name = "默认名称"
    # todo: 按照url过滤一遍
    if 'choice' in request.POST:
        data = request.POST['data']
        data = json.loads(data)
        if len(data) == 0:
            return HttpResponse('0')
        else:
            return HttpResponse('1')

    if 'try' in request.POST:
        io_list = request.POST['io_list']  # 出入参
        io_list = json.loads(io_list)

        data_list = request.POST['data_list']
        data_list = json.loads(data_list)
        if trial_test(data_list, io_list, username):
            return HttpResponse("1")
        else:
            return HttpResponse("0")

    if 'create' in request.POST:
        case_name = request.POST['case_name']
        # case_name不仅要校验空值，还要校验是否唯一
        if case_name == "":
            return HttpResponse("2")
        elif not ManageSql.is_value_only(case_name, "case_name", "apitest_apiflowtest"):
            return HttpResponse("4")

        io_list = request.POST['io_list']  # 出入参
        io_list = json.loads(io_list)
        api_io_list = data_to_list(io_list)

        data_list = request.POST['data_list']
        data_list = json.loads(data_list)
        if len(data_list) == 0:
            return HttpResponse("3")

        api_id_list = data_to_list(data_list)
        product_id = Apis.objects.get(id=api_id_list[0][0]).Product_id
        try:
            # 需要创建一个flow_case，包含用例名称、用例描述、产品、测试人
            # 然后创建一个flow_case和api之间的映射记录，包含双方的id，每一条api对应的出入参数
            # 这里如何确定case归属哪个项目？随便取一个api的项目好了

            case_id = ManageSql.write_flow_case_to_sql(case_name, "默认描述", username, product_id)
            ManageSql.write_to_table_api_flow_and_apis(case_id, api_id_list, api_io_list)
            return HttpResponse("1")
        except:
            return HttpResponse("0")
    return render(request, "apitest/form_api_flow_case_cp.html",
                  {"username": username, 'api_to_choose_list': api_to_choose_list,
                   'case_name': case_name})


@login_required
def api_flow_test_manage(request):
    username = request.user
    # 过滤规则筛选的是api_flow_test_list，传给前端的是relation_list
    api_flow_test_list = ApiFlowTest.objects.all()
    product_list = Product.objects.all()

    test_result_list = [0, 1]  # {"0": "测试不通过","1": "测试通过"}
    selected_test_result = selected_product_id = -1  # 默认是-1 表示全选
    test_result = False

    if 'selected_test_result' in request.GET:
        api_flow_test_list, selected_test_result, selected_product_id = model_list_filter(request.GET,
                                                                                          api_flow_test_list)

    if request.method == 'POST':
        api_flow_test_list, selected_test_result, selected_product_id = model_list_filter(request.POST,
                                                                                          api_flow_test_list)
        if 'run_test' in request.POST:
            test_result = flow_case_test(api_flow_test_list, username)

    case_id_list = list(api_flow_test_list.values_list('id', flat=True))
    relation_list = ApiFlowAndApis.objects.filter(ApiFlowTest_id__in=case_id_list)
    list_count, relation_page_list = paginator(request, relation_list, 10)
    return render(request, "apitest/api_flow_test_manage.html",
                  {"username": username, "relation_list": relation_page_list,
                   "api_flow_test_counts": list_count, "product_list": product_list,
                   'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                   'selected_product_id': selected_product_id, "test_result": test_result})


def flow_case_test(api_flow_test_list, tester):
    """
    多个流程case的测试
    :param tester:
    :param api_flow_test_list: 流程case的list
    :return:
    """
    multiple_case_list = []
    print("api_flow_test_list:", api_flow_test_list)
    one_case_id = api_flow_test_list.values_list("id", flat=True)[0]
    one_api_id = ApiFlowAndApis.objects.filter(ApiFlowTest_id=one_case_id).values_list("Apis_id", flat=True)[0]
    product_id = Apis.objects.get(id=one_api_id).Product_id
    host = ManageSql.get_host_of_product(product_id)
    print("product_id:", product_id)
    for case in api_flow_test_list:
        relations = ApiFlowAndApis.objects.filter(ApiFlowTest_id=case.id)
        io_list = []

        for relation in relations:
            io_list.append([relation.output_parameter, relation.input_parameter])

        id_list = relations.values_list("Apis_id", flat=True)
        api_list = Apis.objects.filter(id__in=id_list)
        case_list = model_list_to_case_list(api_list)
        multiple_case_list.append([case_list, io_list, host])
    test_result = TestCaseRequest(tester).flow_api_case_test(multiple_case_list)
    return test_result


@login_required
def apis_manage(request):
    """
    单一接口页面管理
    :param request:
    :return:
    """
    username = request.user
    product_list = Product.objects.all()
    api_list = Apis.objects.all()
    test_result_list = [0, 1]  # {"0": "测试不通过","1": "测试通过"}
    selected_test_result = selected_product_id = -1  # 默认是-1 表示全选

    if 'selected_test_result' in request.GET:
        api_list, selected_test_result, selected_product_id = model_list_filter(request.GET, api_list)

    if request.method == 'POST':
        # 上面的值传来的是对的
        api_list, selected_test_result, selected_product_id = model_list_filter(request.POST, api_list)
        if 'run_test' in request.POST:
            test_case(api_list, username)

    apis_count, apis_page_list = paginator(request, api_list, 6)
    return render(request, 'apitest/apis_manage.html',
                  {'api_list': apis_page_list, "product_list": product_list, 'username': username,
                   'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                   'selected_product_id': selected_product_id, 'apis_count': apis_count})


def test_case(model_list, tester):
    """
    根据筛选出来的list来执行测试（单接口测试）
    :param model_list: QuerySet类型
    :return:
    """
    case_list = model_list_to_case_list(model_list)

    # 获取host，取一个case的host即可
    product_id = Apis.objects.get(id=case_list[0][0]).Product_id
    host = ManageSql().get_host_of_product(product_id)

    # 进行测试
    tester = TestCaseRequest(tester)
    case_list = tester.single_api_test(case_list, host)

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
    username = request.user
    root = os.path.abspath(".")
    filepath = os.path.join(root, "apitest/templates/report")
    # 所有的测试报告都在filepath内，将目录下所有的文件拼成一个list，每个list包含[文件名，测试类型，创建时间，测试结果，测试人]
    file_list = [[file, file.split("_")[0], file.split("_")[1], file.split("_")[2], file.split("_")[3]] for file in listdir(filepath) if file != "__init__.py"]
    # 按照list中第三个内容倒序排序（此处是创建时间）
    file_list = sorted(file_list, key=lambda x: x[2], reverse=True)

    # 过滤筛选
    test_result_list = ["0", "1"]  # {"0": "测试不通过","1": "测试通过"}
    test_type_list = ["单接口测试", "流程接口测试"]  # {"0": "单接口测试","1": "流程接口测试"}
    selected_test_type = selected_test_result = -1  # 默认是-1 表示全选

    if 'selected_test_result' in request.GET:
        file_list, selected_test_type, selected_test_result = report_list_filter(request, file_list)

    if 'filter' in request.POST:
        file_list, selected_test_type, selected_test_result = report_list_filter(request, file_list)

    return render(request, "apitest/report.html",
                  {"username": username, "file_list": file_list, "report_count": len(file_list),
                   "test_result_list": test_result_list, "test_type_list": test_type_list,
                   "selected_test_type": selected_test_type, "selected_test_result": selected_test_result})


@login_required
def test_report_detail(request, report_name):
    return render(request, "report/" + report_name, {})


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
    api_list = Apis.objects.filter(api_name__icontains=apiname)
    api_count, api_page_list = paginator(request, api_list, 10)
    return render(request, "apitest/apis_manage.html", {"user": username, "api_list": api_page_list,
                                                        "apis_count": api_count})


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
                  {'error': error, 'data': source, "username": username, "apis_list": apis_page_list,
                   "apis_count": apis_count})


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
    product_id = Apis.objects.get(id=case_list[0][0]).Product_id
    ManageSql().delete_variables_in_sql()
    ManageSql().write_variables_to_sql(product_id, variables_dict)


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


def report_list_filter(request, list_to_filter):
    selected_test_type = request.POST.get('selected_test_type')
    selected_test_result = request.POST.get('selected_test_result')
    list_filtered = list_to_filter

    if selected_test_type != '-1':
        list_filtered = [item for item in list_filtered if item[1] == selected_test_type]
    if selected_test_result != '-1':
        list_filtered = [item for item in list_filtered if item[3] == ("PASS" if selected_test_result == "1" else "FAIL")]
    return list_filtered, selected_test_type, selected_test_result


def model_list_filter(request, list_to_filter):
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
        list_filtered = list_filtered.filter(test_result=True if selected_test_result == '1' else False)

    return list_filtered, int(selected_test_result), int(selected_product_id)


def data_to_list(data):
    """
    把前端传过来的string，转化成python可用的list（前端每个值都是用逗号分隔的）
    :param data:
    :return:
    """
    data_list = []
    for item in data:
        item = item.split(',')  # 最后多一个空项
        data_list.append(item)
    for item in data_list:
        item.pop()
    return data_list


def trial_test(data_list, io_list, tester):
    """
    场景测试case的试测
    :param tester:
    :param data_list: data_list是前端传来的数据，包含api的id
    :param io_list: 出入参信息
    :return:
    """
    data_list = data_to_list(data_list)
    api_io_list = data_to_list(io_list)
    api_id_list = []
    for item in data_list:
        api_id_list.append(int(item[0]))

    api_to_test_list = Apis.objects.filter(id__in=api_id_list)
    product_id = Apis.objects.get(id=api_id_list[0]).Product_id
    host = ManageSql.get_host_of_product(product_id)
    case_list = model_list_to_case_list(api_to_test_list)
    return TestCaseRequest(tester).flow_api_single_case_test(api_io_list, case_list, host)


def save_case_locally(case_list, host):
    pass


def model_list_to_case_list(model_list):
    """
    把Django的数据库查询集合，转化成python可用的list
    :param model_list: 实际上是一个api_list
    :return:
    """
    case_list = []
    for case in model_list:
        case_list.append([case.id, case.api_url, case.api_method, ast.literal_eval(case.api_param_value),
                          ast.literal_eval(case.api_body_value),
                          case.api_expect_status_code, case.api_expect_response])
    return case_list
