# Generated by Django 3.0.6 on 2020-06-13 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0005_auto_20200613_1901'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='bmi',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='person',
            name='height',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='person',
            name='weight',
            field=models.FloatField(default=0),
        ),
    ]
