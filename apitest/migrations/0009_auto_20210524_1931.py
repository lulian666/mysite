# Generated by Django 3.1.7 on 2021-05-24 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0008_auto_20210524_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiflowandapis',
            name='create_time',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='apiflowtest',
            name='create_time',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='创建时间'),
        ),
    ]