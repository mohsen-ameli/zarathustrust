# Generated by Django 3.2.13 on 2022-07-02 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0044_rename_transaction_history_transactionhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='money_to_send',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
