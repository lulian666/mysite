from django.db import models


# Create your models here.
class Product(models.Model):
    product_name = models.CharField('产品名称', max_length=64)
    product_desc = models.CharField('产品描述', max_length=200)
    product_host = models.CharField('域名', max_length=200, null=True)
    exclude_api = models.CharField('排除接口', max_length=2000, null=True)
    create_time = models.DateTimeField('创建时间', auto_now=True)

    class Meta:
        verbose_name = '产品管理'
        verbose_name_plural = '产品管理'

    def __str__(self):
        return self.productname