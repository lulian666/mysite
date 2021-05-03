from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'account'
urlpatterns = [
    # path(r'login/', views.LoginUser.as_view(), name='user_login'),
    path(r'login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='user_login'),
    path(r'logout/', auth_views.LogoutView.as_view(template_name='account/login.html'), name='user_logout'),
]