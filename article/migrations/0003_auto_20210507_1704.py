# Generated by Django 3.1.7 on 2021-05-07 17:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_articlepost'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articlepost',
            options={'ordering': ['-updated']},
        ),
        migrations.AlterField(
            model_name='articlepost',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 7, 17, 4, 30, 102315)),
        ),
    ]
