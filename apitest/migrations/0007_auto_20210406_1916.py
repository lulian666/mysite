# Generated by Django 3.1.7 on 2021-04-06 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0006_auto_20210406_1912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apis',
            name='apiresult',
            field=models.CharField(max_length=200, null=True, verbose_name='预期结果'),
        ),
        migrations.AlterField(
            model_name='apistep',
            name='apiresult',
            field=models.CharField(max_length=200, null=True, verbose_name='预期结果'),
        ),
    ]