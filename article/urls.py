from django.urls import path
from . import views

app_name = 'article'
urlpatterns = [
    path('article-column/', views.article_column, name='article_column'),
    path('rename-article-column/', views.rename_article_column, name='rename_article_column'),
]