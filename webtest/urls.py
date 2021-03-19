from django.urls import path

from . import views

app_name = 'webtest'
urlpatterns = [
    path('webcase_manage/', views.webcase_manage, name='webcase_manage'),
    path('webcasestep_manage/', views.webcasestep_manage, name='webcasstep_manage'),
    path('websearch/', views.websearch, name='websearch'),
    path('webcasestepsearch/', views.webstepsearch, name='webstepsearch'),
]