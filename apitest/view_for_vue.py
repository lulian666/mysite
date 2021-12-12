import json

from django.http import HttpResponse

from product.models import Product


def get_products(request):
    products = Product.objects.all().values("product_name", "id")
    products_dict = [entry for entry in products]
    print(products_dict)
    print(type(products_dict))
    json_data = json.dumps(products_dict)
    print(json_data)
    print(type(json_data))
    return HttpResponse(json_data, content_type='application/json')

