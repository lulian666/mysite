from django.db import models
from product.models import Product


# Create your models here.
class ApiFlowTest(models.Model):
    Product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)
    case_name = models.CharField('流程接口名称', max_length=64)
    case_desc = models.CharField('描述', max_length=64)
    case_tester = models.CharField('测试负责人', max_length=16)
    case_test_result = models.BooleanField('测试结果', null=True)
    create_time = models.DateTimeField('创建时间', auto_now=True, null=True)

    class Meta:
        verbose_name = '流程场景接口'
        verbose_name_plural = '流程场景接口'

    def __str__(self):
        return self.case_name


class ApiFlowAndApis(models.Model):
    ApiFlowTest = models.ForeignKey('apitest.ApiFlowTest', on_delete=models.CASCADE, null=True)
    Apis = models.ForeignKey('apitest.Apis', on_delete=models.CASCADE, null=True)
    output_parameter = models.CharField('需保存参数', max_length=100, null=True)
    input_parameter = models.CharField('需传入参数', max_length=100, null=True)
    execution_order = models.IntegerField('执行顺序', null=True)
    create_time = models.DateTimeField('创建时间', auto_now=True, null=True)

    class Meta:
        verbose_name = '流程接口用例和单一接口映射'
        verbose_name_plural = '流程接口用例和单一接口映射'

# class ApiStep(models.Model):
#     ApiFlowTest = models.ForeignKey('apitest.ApiFlowTest', on_delete=models.CASCADE, null=True)
#     api_name = models.CharField('接口名称', max_length=100)
#     api_url = models.CharField('url 地址', max_length=200)
#     api_step = models.CharField('测试步骤', max_length=100, null=True)
#     api_param_value = models.CharField('请求参数和值', max_length=800)
#     REQUEST_METHOD = (('get', 'get'), ('post', 'post'), ('put', 'put'), ('delete', 'delete'), ('patch', 'patch'))
#     api_method = models.CharField(verbose_name='请求方法', choices=REQUEST_METHOD, default='get', max_length=200, null=True)
#     api_result = models.CharField('预期结果', max_length=200, null=True)
#     api_response = models.CharField('响应数据', max_length=5000, null=True)
#     api_status = models.BooleanField('是否通过')
#     create_time = models.DateTimeField('创建时间', auto_now=True)
#
#     def __str__(self):
#         return self.api_name


class Apis(models.Model):
    Product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)
    api_name = models.CharField('接口名称', max_length=100)
    api_url = models.CharField('url 地址', max_length=200)
    api_param_value = models.CharField('请求参数', max_length=500, null=True)
    api_body_value = models.CharField('请求body', max_length=1000, null=True)
    REQUEST_METHOD = (('get', 'get'), ('post', 'post'), ('put', 'put'), ('delete', 'delete'), ('patch', 'patch'))
    api_method = models.CharField('请求方法', choices=REQUEST_METHOD, default='0', max_length=200)
    api_expect_response = models.CharField('预期结果', max_length=500, null=True)
    api_expect_status_code = models.IntegerField('预期状态码', default=200)
    api_response = models.CharField('测试结果', max_length=1000, null=True)
    api_response_status_code = models.IntegerField('预期状态码', null=True)
    api_status = models.BooleanField('是否通过', null=True)
    create_time = models.DateTimeField('创建时间', auto_now=True, null=True)

    class Meta:
        verbose_name = '单一场景接口'
        verbose_name_plural = '单一场景接口'

    def __str__(self):
        return self.api_name


class Headers(models.Model):
    Product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)
    header_key = models.CharField('变量名', max_length=100)
    header_value = models.CharField('变量值', max_length=1000)

    class Meta:
        verbose_name = 'header'
        verbose_name_plural = 'header'

    def __str__(self):
        return self.header_key


class Variables(models.Model):
    Product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)
    variable_key = models.CharField('变量名', max_length=100)
    variable_value = models.CharField('变量值', max_length=1000, null=True)
    from_api = models.CharField('所属接口', max_length=1000, null=True)

    class Meta:
        verbose_name = '参数'
        verbose_name_plural = '参数'

    def __str__(self):
        return self.variable_key