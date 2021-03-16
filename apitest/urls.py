from django.urls import path

from . import views

app_name = 'apitest'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('test/', views.test, name='test'),
    path('logout/', views.logout, name='logout'),
    path('apitest_manage/',views.apitest_manage, name = 'apitest_manage'),
    path('apistep_manage/',views.apistep_manage, name = 'apistep_manage'),
    path('apis_manage/',views.apis_manage, name = 'apis_manage'),
    path('test_report/',views.test_report, name = 'test_report'),
    path('left/',views.left, name = 'left'),
]