# Generated by Django 2.2 on 2019-10-24 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_auto_20191024_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pay',
            name='appointment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pay', to='appointment.Appointment', verbose_name='预约记录'),
        ),
    ]
