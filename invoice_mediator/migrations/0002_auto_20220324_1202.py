# Generated by Django 2.2 on 2022-03-24 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice_mediator', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group_account',
            name='officeId',
        ),
        migrations.AlterField(
            model_name='group_account',
            name='id',
            field=models.PositiveSmallIntegerField(primary_key=True, serialize=False, verbose_name='Account ID'),
        ),
    ]