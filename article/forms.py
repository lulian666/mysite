from django import forms

from article.models import ArticleColumn


class ArticleColumnForm(forms.ModelForm):
    class Meta:
        model = ArticleColumn
        fields = ['column']
