# Generated by Django 3.1.7 on 2021-05-20 20:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0010_auto_20210520_2046'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apistep',
            old_name='ApiTest',
            new_name='ApiFlowTest',
        ),
    ]
