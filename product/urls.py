from django.urls import path

from . import views

app_name = 'product'
urlpatterns = [
    path('product_manage/', views.product_manage, name='product_manage'),
    # path('add_new_product/', views.add_new_product, name='add_new_product'),
    path('search/', views.search, name='search'),
]