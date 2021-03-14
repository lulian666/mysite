from django.db import models

# Create your models here.
class Webcase(models.Model):
    Product = models.ForeignKey('product.Product',on_delete=models.CASCADE, null=True)
    webcasename = models.CharField('用例名称', max_length=200)
    webtestresult = models.BooleanField('测试结果')
    webtester = models.CharField('测试负责人', max_length=16)
    create_time = models.DateTimeField('创建时间', auto_now=True)

    class Meta:
        verbose_name = 'web 测试用例'
        verbose_name_plural = 'web 测试用例'

    def __str__(self):
        return self.webcasename

class Webcasestep(models.Model):
    Webcase = models.ForeignKey(Webcase,on_delete=models.CASCADE, null=True)
    webcasename = models.CharField('测试用例标题',max_length=200)
    webteststep = models.CharField('测试步骤',max_length=200)
    webtestobjname = models.CharField('测试对象名称描述',max_length=200)
    webfindmethod = models.CharField('定位方式',max_length=200)
    webevelement = models.CharField('控件元素',max_length=800)
    weboptmethod = models.CharField('操作方法',max_length=800)
    webtestdata = models.CharField('测试数据',max_length=200,null=True)
    webtestassertdata = models.CharField('验证数据',max_length=200)
    webtestresult = models.BooleanField('测试结果')
    create_time = models.DateTimeField('创建时间', auto_now=True)

    def __str__(self):
        return self.webcasename