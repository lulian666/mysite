from django.urls import path

from . import views

app_name = 'apptest'
urlpatterns = [
    path('appcase_manage/', views.appcase_manage, name='appcase_manage'),
    path('appcasestep_manage/', views.appcasestep_manage, name='appcasestep_manage'),
]