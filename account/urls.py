from django.urls import path, reverse, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'account'
urlpatterns = [
    # path(r'login/', views.LoginUser.as_view(), name='user_login'),
    path(r'login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='user_login'),
    path(r'logout/', auth_views.LogoutView.as_view(template_name='account/login.html'), name='user_logout'),
    path(r'register/', views.register, name='user_register'),
    path(r'', views.bug, name='bug'),
    path(r'password-change', auth_views.PasswordChangeView.as_view(template_name='account/password_change_form.html', success_url=reverse_lazy('blog:blog_title')), name='password_change'),
    # path(r'password-change', views.ChangePassword.as_view(), name='password_change'),
    path(r'password-change-done', auth_views.PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'), name='password_change_done'),
]