# Generated by Django 3.1.7 on 2021-05-07 17:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0003_auto_20210507_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepost',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 7, 17, 6, 38, 226415)),
        ),
    ]