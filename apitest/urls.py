from django.urls import path

from . import views, function_view, view_for_vue

app_name = 'apitest'
urlpatterns = [
    path('login/', views.login, name='login'),
    # path('home/', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('api_flow_test_manage/', views.api_flow_test_manage, name='api_flow_test_manage'),
    path('form_api_flow_case/', views.form_api_flow_case, name='form_api_flow_case'),
    path('apis_manage/', views.apis_manage, name='apis_manage'),
    path('testAll/', views.testAll, name='testAll'),
    path('test_report/', views.test_report, name='test_report'),
    path('test_report/<report_name>', views.test_report_detail, name='test_report_detail'),
    # path('left/', views.left, name='left'),
    path('apisearch/', views.search, name='search'),
    path('apissearch/', views.apis_search, name='apissearch'),
    path('welcome/', views.welcome, name='welcome'),
    path('api_datasource/', views.datasource, name='api_datasource'),
    path('api_header/', views.api_header, name='api_header'),
    path('variables_manage/', views.variables_manage, name='variables_manage'),
    path('change_api_not_for_test/', function_view.change_api_not_for_test, name='change_api_not_for_test'),
    path('mark_variable_for_preparation/', function_view.mark_variable_for_preparation, name='mark_variable_for_preparation'),
    path('update_variable_depend_api/', function_view.update_variable_depend_api, name='update_variable_depend_api'),
    path('update_variable_json_path/', function_view.update_variable_json_path, name='update_variable_json_path'),
    path('debug_variable_preparation/', function_view.debug_variable_preparation, name='debug_variable_preparation'),
    path('show_exclude_info/', function_view.show_exclude_info, name='show_exclude_info'),

    path('getproducts/', view_for_vue.get_products, name='get_products'),
]