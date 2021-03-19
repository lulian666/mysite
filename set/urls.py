from django.urls import path

from . import views

app_name = 'set'
urlpatterns = [
    path('set_manage/', views.set_manage, name='set_manage'),
    path('user/', views.set_user, name='user'),
    path('search/', views.search, name='search'),
    path('usersearch/', views.usersearch, name='usersearch'),
    ]