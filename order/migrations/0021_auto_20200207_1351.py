# Generated by Django 2.2.7 on 2020-02-07 05:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0020_auto_20200207_1306'),
    ]

    operations = [
        migrations.RenameField(
            model_name='charge',
            old_name='user',
            new_name='group',
        ),
    ]
