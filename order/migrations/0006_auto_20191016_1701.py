# Generated by Django 2.2 on 2019-10-16 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_auto_20191016_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charge',
            name='rest_money',
            field=models.IntegerField(editable=False, verbose_name='剩余金额'),
        ),
    ]
