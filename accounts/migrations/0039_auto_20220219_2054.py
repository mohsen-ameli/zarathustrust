# Generated by Django 3.2.12 on 2022-02-20 01:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0038_auto_20220219_2054'),
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
