from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from apitest.common.case_test import TestCaseRequest
from apitest.models import Apis, Variables
from apitest.views import renew_variable
from product.models import Product


@login_required
@csrf_exempt
def change_api_not_for_test(request):
    is_not_for_test = request.POST.get('is_not_for_test')
    try:
        case_id = request.POST.get('case_id')
        api = Apis.objects.get(id=case_id)
        api.not_for_test = True if is_not_for_test == 'true' else None
        api.save()
        print('status now:', api.not_for_test)
        return HttpResponse('1')
    except:
        return HttpResponse('0')


@login_required
@csrf_exempt
def mark_variable_for_preparation(request):
    mark_for_preparation = request.POST.get('mark_for_preparation')
    try:
        variable_id = request.POST.get('variable_id')
        variable = Variables.objects.get(id=variable_id)
        variable.variable_need_preparation = True if mark_for_preparation == 'true' else None
        variable.save()
        print('status now:', variable.variable_need_preparation)
        return HttpResponse('1')
    except:
        return HttpResponse('0')


@login_required
@csrf_exempt
def update_variable_depend_api(request):
    try:
        depend_api_id = request.POST.get('depend_api_id')
        api = Apis.objects.get(id=depend_api_id)
        variable_id = request.POST.get('variable_id')
        variable = Variables.objects.get(id=variable_id)
        # 要检查一下这两个的 product id 是不是一样
        if api.Product_id == variable.Product_id:
            variable.variable_depend_api_id = depend_api_id
            # 有时前端操作会忘了勾选标记，如果输入了 id，就默认要标记
            variable.variable_need_preparation = True
            variable.save()
            print('variable_depend_api_id:', variable.variable_depend_api_id)
            return HttpResponse(api.api_url)
        else:
            return HttpResponse('2')
    except:
        return HttpResponse('0')


@login_required
@csrf_exempt
def update_variable_json_path(request):
    try:
        json_path = request.POST.get('json_path')
        variable_id = request.POST.get('variable_id')
        variable = Variables.objects.get(id=variable_id)
        variable.variable_reach_json_path = json_path
        variable.save()
        print('variable_reach_json_path:', variable.variable_reach_json_path)
        return HttpResponse('1')
    except:
        return HttpResponse('0')


@login_required
@csrf_exempt
def debug_variable_preparation(request):
    username = request.user
    variable_id = request.POST.get('variable_id')
    product_id = request.POST.get('product_id')
    json_path = request.POST.get('json_path')
    variable = Variables.objects.get(id=variable_id)
    # 警惕，这里用户不一定输入了值
    if not variable.variable_need_preparation or not variable.variable_depend_api_id or not variable.variable_reach_json_path:
        return HttpResponse("0")

    host = Product.objects.get(id=product_id).product_host
    test_manager = TestCaseRequest(username, product_id)
    target_value = renew_variable(variable_id, test_manager, host, json_path=json_path)
    return HttpResponse(target_value)


@login_required
@csrf_exempt
def show_exclude_info(request):
    # 更改下拉菜单时，把已有的内容更新到文本框内
    product_id = request.POST['product_id']
    exclude_data = list(Product.objects.filter(id=product_id).values_list('exclude_api', flat=True))
    return HttpResponse(exclude_data)

