# Generated by Django 3.0.6 on 2020-06-13 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0008_auto_20200613_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appointment.Schedule', unique=True),
        ),
    ]