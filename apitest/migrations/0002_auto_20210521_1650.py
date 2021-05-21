# Generated by Django 3.1.7 on 2021-05-21 16:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiFlowAndApis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ApiFlowTest', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='apitest.apiflowtest')),
                ('Apis', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='apitest.apis')),
            ],
            options={
                'verbose_name': '流程接口用例和单一接口映射',
                'verbose_name_plural': '流程接口用例和单一接口映射',
            },
        ),
        migrations.DeleteModel(
            name='ApiStep',
        ),
    ]
