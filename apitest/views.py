import ast
import json
import os
from os import listdir

import jsonpath
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import QuerySet, Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from apitest.common.case_collect_data import CaseCollect
from apitest.common.case_readyfortest import CaseReady
from apitest.common.case_test import TestCaseRequest
from apitest.common.header_mange import HeaderManage
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


def logout(request):
    return render(request, 'apitest/login.html')


@login_required(login_url='/account/login/')
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
        is_success, try_refresh_token = trial_test(data_list, io_list, username)
        if is_success and try_refresh_token:
            return HttpResponse("1")
        elif not try_refresh_token:
            return HttpResponse("2")
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


@login_required(login_url='/account/login/')
def api_flow_test_manage(request):
    username = request.user
    # 过滤规则筛选的是api_flow_test_list，传给前端的是relation_list
    api_flow_test_list = ApiFlowTest.objects.all()
    product_list = Product.objects.all()

    test_result_list = [0, 1]  # {"0": "测试不通过","1": "测试通过"}
    selected_test_result = selected_product_id = -1  # 默认是-1 表示全选
    test_result = False
    fail_message =''

    if 'selected_test_result' in request.GET:
        api_flow_test_list, selected_test_result, selected_product_id = model_list_filter(request.GET,
                                                                                          api_flow_test_list)

    if request.method == 'POST':
        api_flow_test_list, selected_test_result, selected_product_id = model_list_filter(request.POST,
                                                                                          api_flow_test_list)
        if 'run_test' in request.POST:
            test_result, try_refresh_token = flow_case_test(api_flow_test_list, username)
            if not try_refresh_token:
                fail_message = '更新token失败，请检查access-token是否已经过期'
    case_id_list = list(api_flow_test_list.values_list('id', flat=True))
    relation_list = ApiFlowAndApis.objects.filter(ApiFlowTest_id__in=case_id_list)
    list_count, relation_page_list = paginator(request, relation_list, 10)
    return render(request, "apitest/api_flow_test_manage.html",
                  {"username": username, "relation_list": relation_page_list,
                   "api_flow_test_counts": list_count, "product_list": product_list,
                   'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                   'selected_product_id': selected_product_id, "test_result": test_result, 'fail_message': fail_message})


def flow_case_test(api_flow_test_list, tester):
    """
    多个流程case的测试
    :param tester:
    :param api_flow_test_list: 流程case的list
    :return:
    """
    multiple_case_list = []
    one_case_id = api_flow_test_list.values_list("id", flat=True)[0]
    one_api_id = ApiFlowAndApis.objects.filter(ApiFlowTest_id=one_case_id).values_list("Apis_id", flat=True)[0]
    product_id = Apis.objects.get(id=one_api_id).Product_id
    host = ManageSql.get_host_of_product(product_id)
    for case in api_flow_test_list:
        relations = ApiFlowAndApis.objects.filter(ApiFlowTest_id=case.id)
        io_list = []

        for relation in relations:
            io_list.append([relation.output_parameter, relation.input_parameter])

        id_list = relations.values_list("Apis_id", flat=True)
        api_list = Apis.objects.filter(id__in=id_list)
        case_list = model_list_to_case_list(api_list)
        multiple_case_list.append([case_list, io_list, host])
    test_result, try_refresh_token = TestCaseRequest(tester).flow_api_case_test(multiple_case_list)
    return test_result, try_refresh_token


# 专门写的对外的接口
@csrf_exempt
def testAll(request):
    if request.method == 'POST':
        selected_product_id = json.loads(request.body)['selected_product_id']
        renew_variables(selected_product_id, 'outsider')
        ManageSql.update_variable_in_case(selected_product_id)
        api_list = Apis.objects.filter(Product_id=selected_product_id).filter(not_for_test__isnull=True)
        print(len(api_list))
        result, try_refresh_token = test_case(api_list, 'from jenkins')
        if try_refresh_token:
            # api_list 里有失败的那就说明测试失败了，统计失败的有多少
            success_case_num = len(api_list.filter(test_result='1'))
            fail_case_num = len(api_list.filter(test_result='0'))
            print('fail_case_num:', fail_case_num)
            if fail_case_num > 0:
                return HttpResponse(content='有测试失败的 case', content_type='application/json', status=202)
            else:
                return HttpResponse(content='测试成功 0 失败', content_type='application/json', status=200)
        else:
            return HttpResponse(content='token 刷新失败，没有进行测试', content_type='application/json', status=400)


@login_required(login_url='/account/login/')
@csrf_exempt
def apis_manage(request):
    """
    单一接口页面管理
    :param request:
    :return:
    """
    username = request.user
    product_list = Product.objects.all()
    api_list = Apis.objects.filter(not_for_test__isnull=True)
    test_result_list = [0, 1]  # {"0": "测试不通过","1": "测试通过"}
    selected_test_result = selected_product_id = -1  # 默认是-1 表示全选
    show_not_for_test = ''

    if 'selected_test_result' in request.GET:
        show_not_for_test = request.GET.get("show_not_for_test")
        if show_not_for_test == 'show_not_for_test':
            api_list = Apis.objects.all()
        api_list, selected_test_result, selected_product_id = model_list_filter(request.GET, api_list)

    if request.method == 'POST':
        show_not_for_test = request.POST.get("show_not_for_test")
        if show_not_for_test == 'show_not_for_test':
            api_list = Apis.objects.all()
        api_list, selected_test_result, selected_product_id = model_list_filter(request.POST, api_list)
        if 'run_test' in request.POST:
            if int(selected_product_id) == -1:
                fail_message = '还没选择项目'
                apis_count, apis_page_list = paginator(request, api_list, 12)
                return render(request, 'apitest/apis_manage.html',
                              {'api_list': apis_page_list, "product_list": product_list, 'username': username,
                               'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                               'selected_product_id': selected_product_id, 'apis_count': apis_count, 'fail_message': fail_message})
            elif len(HeaderManage.read_header(int(selected_product_id))) == 0:
                apis_count, apis_page_list = paginator(request, api_list, 12)
                fail_message = '这个项目还没有配置 header 哦！'
                return render(request, 'apitest/apis_manage.html',
                              {'api_list': apis_page_list, "product_list": product_list, 'username': username,
                               'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                               'selected_product_id': selected_product_id, 'apis_count': apis_count, 'fail_message': fail_message})
            else:
                # 先做数据准备这一步，所有标记了 variable_need_preparation 的都需要准备，还要考虑数据准备失败的情况
                renew_variables(selected_product_id, username)
                # 用最新的 variables 去刷新一边 case 中的参数，可借用已存在的函数
                ManageSql.update_variable_in_case(selected_product_id)
                # 这里加一遍过滤，not_for_test字段是1的不参与测试
                api_list = api_list.filter(not_for_test__isnull=True)
                result, try_refresh_token = test_case(api_list, username)
                fail_message = '更新token失败，请检查access-token是否已经过期'
                if not try_refresh_token:
                    apis_count, apis_page_list = paginator(request, api_list, 12)
                    return render(request, 'apitest/apis_manage.html',
                                  {'api_list': apis_page_list, "product_list": product_list, 'username': username,
                                   'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                                   'selected_product_id': selected_product_id, 'apis_count': apis_count, 'fail_message': fail_message})
            # 以下是跳转报告列表页所需数据
            root = os.path.abspath(".")
            filepath = os.path.join(root, "apitest/templates/report")
            # 所有的测试报告都在filepath内，将目录下所有的文件拼成一个list，每个list包含[文件名，测试类型，创建时间，测试结果，测试人]
            file_list = [[file, file.split("_")[0], file.split("_")[1], file.split("_")[2], file.split("_")[3]] for file in
                         listdir(filepath) if file != "__init__.py"]
            # 按照list中第三个内容倒序排序（此处是创建时间）
            file_list = sorted(file_list, key=lambda x: x[2], reverse=True)
            test_type_list = ["单接口测试", "流程接口测试"]  # {"0": "单接口测试","1": "流程接口测试"}
            selected_test_type = selected_test_result = -1  # 默认是-1 表示全选
            return render(request, "apitest/report.html",
                          {"username": username, "file_list": file_list, "report_count": len(file_list),
                           "test_result_list": test_result_list, "test_type_list": test_type_list,
                           "selected_test_type": selected_test_type, "selected_test_result": selected_test_result,
                           "list_count": len(file_list)})
        elif 'debug' in request.POST:
            case_id = request.POST.get('case_id')
            api_list = Apis.objects.filter(id=int(case_id))
            result, try_refresh_token = test_case(api_list, username)
            show_result = '状态码：' + str(result.status_code) + '\n' + '返回结果：' + result.text
            if try_refresh_token:
                return HttpResponse(show_result)
            else:
                return HttpResponse('token 过期')
    apis_count, apis_page_list = paginator(request, api_list, 12)
    return render(request, 'apitest/apis_manage.html',
                  {'api_list': apis_page_list, "product_list": product_list, 'username': username,
                   'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                   'selected_product_id': selected_product_id, 'apis_count': apis_count,
                   'show_not_for_test': show_not_for_test})


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
    tester = TestCaseRequest(tester, product_id)
    result, case_list, try_refresh_token = tester.single_api_test(case_list, host)

    # 用pytest进行测试
    # save_case_locally(case_list, host)
    #
    # root = os.path.abspath('.')
    # file = os.path.join(root, 'apitest')
    # cmd = 'py.test -s -v %s' % file
    # os.system(cmd)

    # 将测试结果更新数据库（如果没有遇到401问题）
    if try_refresh_token:
        ManageSql.update_case_to_sql(case_list)
    return result, try_refresh_token


@login_required(login_url='/account/login/')
def test_report(request):
    username = request.user
    root = os.path.abspath(".")
    filepath = os.path.join(root, "apitest/templates/report")
    # 所有的测试报告都在filepath内，将目录下所有的文件拼成一个list，每个list包含[文件名，测试类型，创建时间，测试结果，测试人]
    file_list = [[file, file.split("_")[0], file.split("_")[1], file.split("_")[2], file.split("_")[3]] for file in
                 listdir(filepath) if file != "__init__.py"]
    # 按照list中第三个内容倒序排序（此处是创建时间）
    file_list = sorted(file_list, key=lambda x: x[2], reverse=True)

    # 过滤筛选
    test_result_list = ["0", "1"]  # {"0": "测试不通过","1": "测试通过"}
    test_type_list = ["单接口测试", "流程接口测试"]  # {"0": "单接口测试","1": "流程接口测试"}
    selected_test_type = selected_test_result = -1  # 默认是-1 表示全选

    # 这里备注是因为Django的分页只能对只能对QuerySet类型，这里还没想到解决办法
    # if 'selected_test_result' in request.GET:
    #     file_list, selected_test_type, selected_test_result = report_list_filter(request, file_list)

    if 'filter' in request.POST:
        file_list, selected_test_type, selected_test_result = report_list_filter(request, file_list)

    # list_count, file_page_list = paginator(request, file_list, 10)
    return render(request, "apitest/report.html",
                  {"username": username, "file_list": file_list, "report_count": len(file_list),
                   "test_result_list": test_result_list, "test_type_list": test_type_list,
                   "selected_test_type": selected_test_type, "selected_test_result": selected_test_result,
                   "list_count": len(file_list)})


@login_required(login_url='/account/login/')
def test_report_detail(request, report_name):
    return render(request, "report/" + report_name, {})


@login_required(login_url='/account/login/')
def search(request):
    username = request.session.get('user', '')
    search_apitestname = request.GET.get("apitestname", "")
    apitest_list = ApiFlowTest.objects.filter(apitestname__icontains=search_apitestname)
    return render(request, "apitest/api_flow_test_manage.html", {"user": username, "apitests": apitest_list})


@login_required(login_url='/account/login/')
def apis_search(request):
    username = request.session.get('user', '')
    search_keyword = request.GET.get("search_keyword")
    product_list = Product.objects.all()
    test_result_list = [0, 1]
    api_list = Apis.objects.filter(Q(api_name__icontains=search_keyword) | Q(api_url__icontains=search_keyword))
    api_count, api_page_list = paginator(request, api_list, 10)
    return render(request, "apitest/apis_manage.html", {"user": username, "api_list": api_page_list,
                                                        "apis_count": api_count, "product_list": product_list,
                                                        'test_result_list': test_result_list})


@login_required(login_url='/account/login/')
def welcome(request):
    return render(request, "apitest/welcome.html")


# 处理源数据
@login_required(login_url='/account/login/')
@csrf_exempt
def datasource(request):
    username = request.user
    product_list = Product.objects.all()
    selected_product_id = '-1'
    source = request.POST.get('source', '').strip()
    error = exclude_data = check_info = ''

    if 'selector' in request.POST:
        # 更改下拉菜单时，把已有的内容更新到文本框内
        product_id = request.POST['product_id']
        if product_id != '-1' and product_id is not None:
            exclude_data = list(Product.objects.filter(id=product_id).values_list('exclude_api', flat=True))
            exclude_data = str(exclude_data[0]) if exclude_data[0] is not None else ''
            return HttpResponse(exclude_data)
        else:
            return HttpResponse('')
    elif 'exclude' in request.POST:
        # 提交新的exclude信息到相应的product
        exclude_data = request.POST.get('exclude_api', '').strip()
        selected_product_id = request.POST.get('selected_product_id')
        try:
            product = Product.objects.get(id=selected_product_id)
            product.exclude_api = exclude_data
            product.save()
        except:
            # 需要检查数据格式
            check_info = '没有选择项目（现在选的话先保存你已编辑的内容，否则会丢失！）' if selected_product_id == '-1' else ''

    if 'analysis' in request.POST:
        # 这里要保存已经手动编辑的exclude文本内容，和选择的项目信息
        exclude_data = request.POST.get('exclude_api', '').strip()
        selected_product_id = request.POST.get('selected_product_id')
        if not check_json_format(source):
            error = 'json格式不正确！'
        else:
            error = '正确的json格式～'
    elif 'save' in request.POST:  # 保存，就是写到本地文件里
        root = os.path.abspath('.')  # 获取当前工作目录路径
        if not check_json_format(source):
            error = 'json格式不正确！'
        elif source != "{}":
            error = '正确的json格式～'
            filepath = os.path.join(root, 'apitest/config/temp.json')
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(source))
            f.close()
            # 把接口里的变量保存下来
            selected_product_id = request.POST.get('selected_product_id')
            if selected_product_id != '-1':
                interfaces_not_wanted = Product.objects.get(id=selected_product_id).exclude_api
                basic_case_list, case_list = CaseCollect().collect_data_accordingly(interfaces_not_wanted, selected_product_id)
                # for case in case_list:
                #     print(case)
                if len(basic_case_list) == 0:
                    error = '未解析出case，可能这种格式暂不支持，或者选择的项目不匹配此格式'
                else:
                    save_variables_to_sql(selected_product_id, basic_case_list)
                    variables_list = Variables.objects.filter(Product_id=selected_product_id)
                    # 接口也保存下来
                    new_case_list = CaseReady().data_form(selected_product_id, 3, 4, case_list, variables_list)
                    for case in new_case_list:
                        print(len(case), case)
                    # 为了防止重复
                    print('before:', len(new_case_list))
                    no_repeat_case_list = []
                    for one in new_case_list:
                        if one not in no_repeat_case_list:
                            no_repeat_case_list.append(one)
                    print('after', len(no_repeat_case_list))
                    ManageSql.write_case_to_sql(no_repeat_case_list, selected_product_id)

                    variables_count, variables_page_list = paginator(request, variables_list, 12)
                    return render(request, "apitest/variables_manage.html",
                                  {'error': error, 'data': source, "username": username,
                                   "variables": variables_page_list, "variables_count": variables_count,
                                   "product_list": product_list, "selected_product_id": int(selected_product_id)})
            else:
                error = '还没有选择所属项目'
        else:
            error = '请输入有内容的json'
    return render(request, "apitest/datasource_manage.html",
                  {'error': error, 'data': source, 'username': username,
                   'product_list': product_list, 'selected_product_id': int(selected_product_id),
                   'exclude_data': exclude_data, 'check_info': check_info})


# header 管理
@login_required(login_url='/account/login/')
@csrf_exempt
def api_header(request):
    username = request.user
    headers_list = Headers.objects.all()
    product_list = Product.objects.all()
    selected_product_id = -1  # 默认是-1 表示全选
    check_info, new_headers_raw = '', ''

    if 'selected_product_id' in request.GET:
        headers_list, selected_test_result, selected_product_id = model_list_filter(request.GET, headers_list)

    if 'filter' in request.POST:
        headers_list, selected_test_result, selected_product_id = model_list_filter(request.POST, headers_list)

    if 'check' in request.POST:
        new_headers_raw = request.POST['new_headers'].strip()
        selected_product_id = request.POST['selected_product_id']
        if '\n' not in new_headers_raw or ':' not in new_headers_raw:
            check_info = '格式似乎有问题，再检查一下呢'
        else:
            check_info = '看起来是没问题的，添加完了再看看结果吧！'
        headers_list = Headers.objects.filter(Product_id=selected_product_id)

    if 'add' in request.POST:
        new_headers_raw = request.POST['new_headers']
        selected_product_id = request.POST['selected_product_id']
        try:
            selected_product_id = int(selected_product_id)
        except ValueError:
            try:
                selected_product_id = Product.objects.get(product_name=selected_product_id.strip()).id
            except:
                return HttpResponse('0')
        new_headers_list = new_headers_raw.split('\n')
        for header in new_headers_list:
            ManageSql.write_header_to_sql(header.split(':')[0].strip(), header.split(':')[-1].strip(), selected_product_id)
        headers_list = Headers.objects.filter(Product_id=selected_product_id)

    headers_count, headers_page_list = paginator(request, headers_list, 10)
    return render(request, "apitest/api_header.html",
                  {"username": username, "headers": headers_page_list, "selected_product_id": int(selected_product_id),
                   "product_list": product_list, 'check_info': check_info, 'new_headers': new_headers_raw})


# 变量管理
@login_required(login_url='/account/login/')
@csrf_exempt
def variables_manage(request):
    username = request.user
    variables_list = Variables.objects.all()
    product_list = Product.objects.all()
    selected_product_id = '-1'
    null_value_only = ''
    fail_message = ''
    test_result_list = [0, 1]  # {"0": "测试不通过","1": "测试通过"}

    if 'selected_product_id' in request.GET:
        variables_list, selected_product_id, null_value_only = model_list_filter2(request.GET, variables_list)

    if request.method == 'POST':
        if 'change_value' in request.POST:
            new_value = request.POST.get('new_value')
            variable_id = request.POST.get('variable_id')
            set_for_all = request.POST.get('set_for_all')
            variable = Variables.objects.get(id=variable_id)
            try:
                if set_for_all == 'true':
                    variable_name = variable.variable_key
                    product_id = variable.Product_id
                    variables_share_the_same_name = Variables.objects.filter(Product_id=product_id).filter(variable_key=variable_name)
                    for each in variables_share_the_same_name:
                        is_legal, new_value = check_variable_legal_validity(variable.variable_type, new_value)
                        if is_legal:
                            each.variable_value = new_value
                            each.save()
                        else:
                            return HttpResponse("2")
                    return HttpResponse("1")
                else:
                    # oh my dear don't over thinking this. baby steps. start with little things like string and integer
                    # 前端传过来的好像都是string
                    is_legal, new_value = check_variable_legal_validity(variable.variable_type, new_value)
                    if is_legal:
                        variable.variable_value = new_value
                        variable.save()
                        return HttpResponse("1")
                    else:
                        return HttpResponse("2")
            except:
                return HttpResponse("0")
        variables_list, selected_product_id, null_value_only = model_list_filter2(request.POST, variables_list)
        if 'birth' in request.POST:
            selected_product_id = request.POST.get("selected_product_id")
            if int(selected_product_id) != -1:
                ManageSql.update_variable_in_case(selected_product_id)
                # 跳转去单一接口列表页
                product_list = Product.objects.all()
                selected_test_result = -1  # 默认是-1 表示全选
                api_list = Apis.objects.filter(Product_id=selected_product_id)

                apis_count, apis_page_list = paginator(request, api_list, 12)
                return render(request, 'apitest/apis_manage.html',
                              {'api_list': apis_page_list, "product_list": product_list, "username": username,
                               'test_result_list': test_result_list, "selected_test_result": selected_test_result,
                               'selected_product_id': int(selected_product_id), 'apis_count': apis_count})
            else:
                fail_message = '还没选择项目'
    variables_count, variables_page_list = paginator(request, variables_list, 12)
    return render(request, "apitest/variables_manage.html",
                  {"username": username, "variables": variables_page_list, "variables_count": variables_count,
                   "warning": "只点击一次就好，会跳转到用例列表", "product_list": product_list,
                   "selected_product_id": int(selected_product_id), "null_value_only": null_value_only,
                   'fail_message': fail_message})


def check_variable_legal_validity(variable_type, variable_value):
    # 开始校验类型是否正确了，从数据库查看，快鸟和橙有这些类型：
    """
        快鸟：
            string
            integer☑️
            array
            boolean☑️
            object
        橙：
            Object
            String
            number☑️
            Boolean☑️
            ImageFile
            String[]
            Object[]
    """
    is_legal = False
    if variable_type.lower() == 'string':
        # 好像不太好校验，string可以是任何东西，判断是否是integer吧，也不可以，比如有的id，也是string类型
        # try:
        #     int(variable_value)
        #     is_legal = False
        # except:
        #     is_legal = True
        is_legal = True
    elif variable_type.lower() == 'integer' or variable_value == 'number':
        try:
            variable_value = int(variable_value)
            is_legal = True
        except:
            is_legal = False
    elif variable_type.lower() == 'boolean':
        if variable_value.lower() in ['0', '1', "false", "true"]:
            is_legal = True
        else:
            is_legal = False
    else:
        is_legal = True
    return is_legal, variable_value


def save_variables_to_sql(selected_product_id, basic_case_list):
    """
    将temp.json中接口用到的变量都存到数据库里
    :return:
    """
    variables_dict = {}
    for case in basic_case_list:
        if case[4] != {}:  # 处理body的
            variables_dict = search_variables(case[4], case[1], variables_dict)
        elif case[3] != {}:
            variables_dict = search_variables(case[3], case[1], variables_dict)
    ManageSql().write_variables_to_sql(selected_product_id, variables_dict)


def search_variables(case_variables, case_url, variables_dict):
    """
    找出传入的case_variables中有多少个变量
    :param case_variables: 一般传入的是body或者parameters，格式是：
    :param case_url: 一般是接口url，用作接口名称
    :param variables_dict: 
    :return: 
    """
    param_list = []
    for num, key in list(enumerate(case_variables)):
        if 'enum' not in case_variables[key] and 'son' not in case_variables[key]:
            # 如果这个参数的值里面，有enum这个字段，就不需要存了
            # param_list的格式需要从string变成dict，{variable_key:xxx, variable_optional:xxx, variable_type:xxx}
            param_list.append({'variable_key': key, 'variable_optional': not case_variables[key]['required'], 'variable_type': case_variables[key]['type']})
        elif 'son' in case_variables[key]:  # 这里需要处理有son的情况
            for item, value in case_variables[key]['son'].items():
                param_list.append({'variable_key': item, 'variable_optional': not case_variables[key]['son'][item]['required'], 'variable_type': case_variables[key]['son'][item]['type']})
    if len(param_list) >= 0:
        variables_dict.update({case_url: param_list})
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
    if isinstance(page_list, QuerySet):
        page_list = page_list.order_by('id')
    else:
        page_list = sorted(page_list, key=lambda x: x[2], reverse=True)
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
        list_filtered = [item for item in list_filtered if
                         item[3] == ("PASS" if selected_test_result == "1" else "FAIL")]
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

    if selected_product_id != '-1' and selected_product_id is not None:
        list_filtered = list_to_filter.filter(Product_id=selected_product_id)
    if selected_test_result != '-1' and selected_test_result is not None:
        list_filtered = list_filtered.filter(test_result=True if selected_test_result == '1' else False)

    return list_filtered, int(selected_test_result) if selected_test_result is not None else -1, int(selected_product_id)


def model_list_filter2(request, list_to_filter):
    """
    根据项目id和变量值是否为空来过滤
    :param request:
    :param list_to_filter:
    :return:
    """
    selected_product_id = request.get('selected_product_id')
    null_value_only = request.get("null_value_only")
    list_filtered = list_to_filter
    if selected_product_id != '-1':
        list_filtered = list_filtered.filter(Product_id=selected_product_id)
    if null_value_only == "null_value_only":
        list_filtered = list_filtered.filter(variable_value__isnull=True)
    return list_filtered, int(selected_product_id), null_value_only


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
    is_success, try_refresh_token = TestCaseRequest(tester).flow_api_single_case_test(api_io_list, case_list, host)
    return is_success, try_refresh_token


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
                          case.api_expect_status_code, case.api_expect_response, json.loads(case.api_response_last_time)])
    return case_list


def renew_variables(selected_product_id, username):
    print('renewing variables......')
    variables_to_renew = Variables.objects.filter(Product_id=selected_product_id).filter(variable_need_preparation__isnull=False)
    for variable in variables_to_renew:
        renew_variable(variable.id, username)


def renew_variable(variable_id, username):
    try:
        variable = Variables.objects.get(id=variable_id)
        # 其实这里就是要去执行一个单接口测试，利用已有的函数实现
        case_id = variable.variable_depend_api_id
        api_list = Apis.objects.filter(id=int(case_id))
        result, try_refresh_token = test_case(api_list, username)
    except:
        return "0"
    if try_refresh_token:
        try:
            target_value = jsonpath.jsonpath(result.json(), variable.variable_reach_json_path)[0]
        except:
            target_value = '没有取出数据，请检查 json path 保存了吗？'
        # print('debug:', target_value, type(target_value))
        variable.variable_value = target_value
        variable.save()
        print('one variable renewed......')
        return target_value
    else:
        return "token 过期"
