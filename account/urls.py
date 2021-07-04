from django.urls import path, reverse, reverse_lazy, re_path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'account'
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='user_login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='account/login.html'), name='user_logout'),
    path('register/', views.register, name='user_register'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='account/password_change_form.html', success_url=reverse_lazy('blog:blog_title')), name='password_change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset_form.html', subject_template_name='account/password_reset_subject.txt', email_template_name='account/password_reset_email.html', success_url=reverse_lazy('account:password_reset_done')), name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/(<uidb64>)/(<token>)/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html', success_url=reverse_lazy('account:password_reset_complete')), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),
    path('my-information/', views.myself, name='my_information'),
    path('edit-my-information/', views.myself_edit, name='edit_my_information'),
    path('my-image/', views.my_image, name='my_image'),
]