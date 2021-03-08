from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login),
    path('home/', views.home),
    path('test/', views.test),
]