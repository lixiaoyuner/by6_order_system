# Generated by Django 2.2 on 2019-10-24 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_auto_20191022_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charge',
            name='remarks',
            field=models.TextField(default='', verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='pay',
            name='remarks',
            field=models.TextField(default='', verbose_name='备注'),
        ),
    ]
