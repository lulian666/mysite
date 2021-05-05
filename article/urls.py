from django.urls import path
from . import views

app_name = 'article'
urlpatterns = [
    path('article-column/', views.article_column, name='article_column'),
]