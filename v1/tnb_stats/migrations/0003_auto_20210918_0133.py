# Generated by Django 3.1.8 on 2021-09-17 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tnb_stats', '0002_auto_20210918_0124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stat',
            name='richest',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='stat',
            name='shift',
            field=models.IntegerField(),
        ),
    ]
