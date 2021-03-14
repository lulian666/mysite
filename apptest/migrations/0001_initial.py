# Generated by Django 3.1.7 on 2021-03-14 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0002_auto_20210313_2005'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appcase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appcasename', models.CharField(max_length=200, verbose_name='用例名称')),
                ('apptestresult', models.BooleanField(verbose_name='测试结果')),
                ('apptester', models.CharField(max_length=16, verbose_name='测试负责人')),
                ('create_time', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
                ('Product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
            options={
                'verbose_name': 'app 测试用例',
                'verbose_name_plural': 'app 测试用例',
            },
        ),
        migrations.CreateModel(
            name='Appcasestep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appteststep', models.CharField(max_length=200, verbose_name='测试步骤')),
                ('apptestobjname', models.CharField(max_length=200, verbose_name='测试对象名称描述')),
                ('appfindmethod', models.CharField(max_length=200, verbose_name='定位方式')),
                ('appevelement', models.CharField(max_length=200, verbose_name='控件元素')),
                ('appoptmethod', models.CharField(max_length=200, verbose_name='操作方法')),
                ('apptestdata', models.CharField(max_length=200, null=True, verbose_name='测试数据')),
                ('appassertdata', models.CharField(max_length=200, verbose_name='验证数据')),
                ('apptestresult', models.BooleanField(verbose_name='测试结果')),
                ('create_time', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
                ('Appcase', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='apptest.appcase')),
            ],
        ),
    ]
