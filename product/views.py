from django.shortcuts import render

# Create your views here.
from product.models import Product


def product_manage(request):
    username = request.session.get('user','')
    product_list = Product.objects.all()
    return render(request, 'product/product_manage.html', {"username": username, "products": product_list})