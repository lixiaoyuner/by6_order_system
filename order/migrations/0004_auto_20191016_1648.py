# Generated by Django 2.2 on 2019-10-16 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_auto_20191016_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paytype',
            name='value',
            field=models.IntegerField(default=1, verbose_name='加班费单价（维护），*元/小时'),
        ),
    ]
