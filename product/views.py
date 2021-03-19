from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from product.models import Product


def product_manage(request):
    username = request.session.get('user','')
    product_list = Product.objects.all()
    return render(request, 'product/product_manage.html', {"username": username, "products": product_list})

@login_required
def search(request):
    username = request.session.get('user','')
    search_productname = request.GET.get("productname","")
    product_list = Product.objects.filter(productname__icontains=search_productname)
    return render(request,"product/product_manage.html",{"user":username,"products":product_list})