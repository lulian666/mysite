from django.urls import path

from . import views

app_name = 'apptest'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('test/', views.test, name='test'),
    path('logout/', views.logout, name='logout'),
]