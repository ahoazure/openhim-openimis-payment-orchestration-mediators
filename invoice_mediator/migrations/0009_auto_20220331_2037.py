# Generated by Django 2.2 on 2022-03-31 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice_mediator', '0008_auto_20220331_1904'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personal_account',
            name='person',
        ),
        migrations.RemoveField(
            model_name='personal_account',
            name='productName',
        ),
        migrations.AddField(
            model_name='personal_account',
            name='clientID',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Client ID'),
        ),
        migrations.AddField(
            model_name='personal_account',
            name='clientName',
            field=models.CharField(blank=True, max_length=45, null=True),
        ),
    ]
