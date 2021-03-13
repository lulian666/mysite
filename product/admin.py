from django.contrib import admin
from product.models import Product
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display =  ['productname', 'productdesc', 'producter', 'create_time', 'id']
    list_filter = ['create_time']
    search_fields = ['productname', 'productdesc']
    list_per_page = 10

admin.site.register(Product, ProductAdmin)