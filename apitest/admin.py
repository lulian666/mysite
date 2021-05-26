from django.contrib import admin
from apitest.models import ApiFlowTest, Apis, Headers, Variables, ApiFlowAndApis


# Register your models here.

class ApiFlowAndApisAdmin(admin.TabularInline):
    list_display = ['ApiFlowTest_id', 'Apis_id', 'execution_order', 'output_parameter', 'input_parameter', 'create_time', 'id']
    model = ApiFlowAndApis
    extra = 1


class ApiFlowTestAdmin(admin.ModelAdmin):
    list_display = ['case_name', 'case_tester', 'test_result', 'create_time', 'id']
    inlines = [ApiFlowAndApisAdmin]
    search_fields = ['case_name', 'case_tester']
    list_filter = ['create_time', 'Product_id', 'test_result']
    list_per_page = 10


admin.site.register(ApiFlowTest, ApiFlowTestAdmin)


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
