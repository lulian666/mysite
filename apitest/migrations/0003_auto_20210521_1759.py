# Generated by Django 3.1.7 on 2021-05-21 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0002_auto_20210521_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiflowandapis',
            name='execution_order',
            field=models.IntegerField(max_length=100, null=True, verbose_name='执行顺序'),
        ),
        migrations.AddField(
            model_name='apiflowandapis',
            name='param_to_save',
            field=models.CharField(max_length=100, null=True, verbose_name='需保存参数'),
        ),
        migrations.AddField(
            model_name='apiflowandapis',
            name='param_to_use',
            field=models.CharField(max_length=100, null=True, verbose_name='需传入参数'),
        ),
    ]