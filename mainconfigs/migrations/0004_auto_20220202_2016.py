# Generated by Django 2.2 on 2022-02-02 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainconfigs', '0003_auto_20220202_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configs',
            name='has_port',
        ),
        migrations.RemoveField(
            model_name='configs',
            name='mediator_port',
        ),
        migrations.RemoveField(
            model_name='configs',
            name='mifos_port',
        ),
        migrations.RemoveField(
            model_name='configs',
            name='openhim_port',
        ),
        migrations.RemoveField(
            model_name='configs',
            name='openimis_port',
        ),
    ]
