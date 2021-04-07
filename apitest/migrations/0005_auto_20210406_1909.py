# Generated by Django 3.1.7 on 2021-04-06 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0004_auto_20210406_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apis',
            name='apistatus',
            field=models.BooleanField(null=True, verbose_name='是否通过'),
        ),
        migrations.AlterField(
            model_name='apistep',
            name='apiresult',
            field=models.CharField(max_length=200, null=True, verbose_name='预期结果'),
        ),
    ]