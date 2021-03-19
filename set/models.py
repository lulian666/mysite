from django.db import models

# Create your models here.
class Set(models.Model):
    setname = models.CharField('系统名称', max_length=64)
    setvalue = models.CharField('系统设置', max_length=200)

    class Meta:
        verbose_name = '系统设置'
        verbose_name_plural = '系统设置'

    def __str__(self):
        return self.setname

# class User(models.Model):
#     username = models.CharField('用户名称', max_length=64)
#     setvalue = models.CharField('xxx', max_length=200)
#
#     class Meta:
#         verbose_name = '用户名称'
#         verbose_name_plural = '用户名称'
#
#     def __str__(self):
#         return self.username