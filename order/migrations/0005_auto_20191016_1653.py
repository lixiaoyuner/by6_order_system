# Generated by Django 2.2 on 2019-10-16 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_auto_20191016_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charge',
            name='remarks',
            field=models.TextField(blank=True, null=True, verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='pay',
            name='remarks',
            field=models.TextField(blank=True, null=True, verbose_name='备注'),
        ),
    ]
