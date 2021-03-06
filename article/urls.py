from django.urls import path
from . import views, list_views

app_name = 'article'
urlpatterns = [
    path('article-column/', views.article_column, name='article_column'),
    path('rename-article-column/', views.rename_article_column, name='rename_article_column'),
    path('delete-article-column/', views.delete_article_column, name='delete_article_column'),
    path('article-post/', views.article_post, name='article_post'),
    path('article-list/', views.article_list, name='article_list'),
    path('article-detail/(<id>)/(<slug>)/', views.article_detail, name='article_detail'),
    path('del-article/', views.del_article, name='del_article'),
    path('redit-article/(<article_id>)/', views.redit_article, name='redit_article'),
    path('list-article-title/', list_views.article_titles, name='list_article_title'),
    path('list-article-detail/(<id>)/(<slug>)/', list_views.article_detail, name='list_article_detail'),
    path('list-article-title/(<username>)/', list_views.article_titles, name='list_author_article'),
    path('like-article/', list_views.like_article, name='list_like_article'),
]