# Generated by Django 3.1.7 on 2021-06-02 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0012_auto_20210531_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='apis',
            name='not_for_test',
            field=models.BooleanField(null=True, verbose_name='是否不进行单接口测试'),
        ),
    ]
