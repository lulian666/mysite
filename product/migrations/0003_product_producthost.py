# Generated by Django 3.1.7 on 2021-04-11 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_auto_20210313_2005'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='producthost',
            field=models.CharField(max_length=200, null=True, verbose_name='域名'),
        ),
    ]