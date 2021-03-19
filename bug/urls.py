from django.urls import path

from . import views

app_name = 'bug'
urlpatterns = [
    path('bug_manage/', views.bug_manage, name='bug_manage'),
    path('search/', views.search, name='search'),
]