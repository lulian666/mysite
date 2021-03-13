import datetime

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(needs_autoescape=True)
def my_filter(text, autoescape=True):
    return mark_safe("<li>欢迎你，<a herf=\"#\">haha</a></li>")

@register.simple_tag
def my_tag1(v1, v2, v3):
    return v1 * v2 * v3

@register.simple_tag(takes_context=True)
def try_context(context, anything):
    username = context['username']
    return username + anything

@register.inclusion_tag('apitest/result.html')
def test():
    a = ['first','second','third']
    return {'choices':a}

