# Generated by Django 2.2 on 2022-01-23 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainconfigs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configs',
            name='openhim_user',
            field=models.CharField(max_length=200, verbose_name='Username'),
        ),
    ]
