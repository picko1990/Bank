# Generated by Django 3.1.3 on 2021-01-08 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('self_configurations', '0002_auto_20201204_1557'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='selfconfiguration',
            name='self_configurations_selfconfiguration_unique_ip_port_proto',
        ),
        migrations.RemoveIndex(
            model_name='selfconfiguration',
            name='self_config_ip_addr_0b8467_idx',
        ),
        migrations.AlterField(
            model_name='selfconfiguration',
            name='ip_address',
            field=models.GenericIPAddressField(unique=True),
        ),
    ]
