# Generated by Django 3.2.12 on 2022-02-20 01:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0036_alter_transaction_history_purpose_of_use'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction_history',
            name='ex_price',
        ),
        migrations.RemoveField(
            model_name='transaction_history',
            name='ex_rate',
        ),
    ]
