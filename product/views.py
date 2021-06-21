from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from apitest.common.managesql import ManageSql
from product.models import Product


@login_required
@csrf_exempt
def product_manage(request):
    username = request.session.get('user', '')
    product_list = Product.objects.all()
    product_count, product_page_list = paginator(request, product_list, 10)
    if 'new_product_name' in request.POST:
        try:
            new_product_name = request.POST['new_product_name']
            new_product_description = request.POST['new_product_description']
            new_product_host = request.POST['new_product_host']

            ManageSql.add_new_product(new_product_name, new_product_description, new_product_host)
            return HttpResponse("1")
        except:
            return HttpResponse("0")
    return render(request, 'product/product_manage.html', {"username": username, "products": product_page_list,
                                                           "product_count": product_count})


@login_required
def search(request):
    username = request.session.get('user','')
    search_productname = request.GET.get("productname","")
    product_list = Product.objects.filter(productname__icontains=search_productname)
    return render(request,"product/product_manage.html",{"user":username,"products":product_list})


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
