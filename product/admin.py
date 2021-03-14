from django.contrib import admin

from apitest.models import Apis
from apptest.models import Appcase
from product.models import Product
# Register your models here.
from webtest.models import Webcase


class ApisAdmin(admin.TabularInline):
    list_display = ['apiname', 'apiurl', 'apiparamvalue', 'apimethod', 'apiresult', 'apistatus', 'create_time', 'id', 'product']
    model = Apis
    extra = 1
    search_field = ['apiname', 'apiurl']
    list_filter = ['create_time']
    list_per_page = 10

class AppcaseAdmin(admin.TabularInline):
    list_display = ['appcasename','apptestresult','create_time','id', 'product']
    model = Appcase
    extra = 1

class WebtestAdmin(admin.TabularInline):
    list_display = ['webcasename','webtestresult','create_time','id', 'product']
    model = Webcase
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display =  ['productname', 'productdesc', 'producter', 'create_time', 'id']
    list_filter = ['create_time']
    search_fields = ['productname', 'productdesc']
    list_per_page = 10
    inlines = [ApisAdmin,AppcaseAdmin,WebtestAdmin]

admin.site.register(Product, ProductAdmin)

