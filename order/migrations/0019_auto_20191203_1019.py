# Generated by Django 2.2 on 2019-12-03 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0018_auto_20191203_0950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chargetype',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='paytype',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
