from django.contrib import admin

# Register your models here.
from article.models import ArticleColumn


class ArticleColumnAdmin(admin.ModelAdmin):
    list_filter = ['column']
    list_display = ['column', 'created', 'user']


admin.site.register(ArticleColumn, ArticleColumnAdmin)