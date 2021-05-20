from django.contrib import admin
from apitest.models import ApiFlowTest, ApiStep, Apis, Headers, Variables


# Register your models here.

class ApistepAdmin(admin.TabularInline):
    list_display = ['api_name', 'api_url', 'api_param_value', 'api_method', 'api_result', 'api_status', 'create_time', 'id', 'api_test']
    model = ApiStep
    extra = 1


class ApitestAdmin(admin.ModelAdmin):
    list_display = ['api_test_name', 'api_tester', 'api_test_result', 'create_time', 'id']
    inlines = [ApistepAdmin]
    search_fields = ['api_test_name']
    list_filter = ['create_time']
    list_per_page = 10


admin.site.register(ApiFlowTest, ApitestAdmin)

class ApisAdmin(admin.TabularInline):
    list_display = ['api_name', 'api_url', 'api_param_value', 'api_method', 'api_result', 'api_status', 'create_time', 'id', 'product']


admin.site.register(Apis)


class HeadersAdmin(admin.ModelAdmin):
    list_display = ['header_key', 'header_value']
    list_filter = ['header_key']
    search_fields = ['header_key']
    list_per_page = 15


class VariableAdmin(admin.ModelAdmin):
    list_display = ['variable_key', 'variable_value', 'from_api', 'Product_id']
    list_filter = ['variable_key']
    search_fields = ['variable_key']
    list_per_page = 15


admin.site.register(Headers, HeadersAdmin)
admin.site.register(Variables, VariableAdmin)

admin.site.site_header = 'AutotestPlat'
admin.site.site_title = 'AutotestPlat'
