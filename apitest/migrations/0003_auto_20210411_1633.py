# Generated by Django 3.1.7 on 2021-04-11 08:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0002_headers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='headers',
            old_name='key',
            new_name='header_key',
        ),
        migrations.RenameField(
            model_name='headers',
            old_name='value',
            new_name='header_value',
        ),
    ]