# Generated by Django 3.2.7 on 2021-12-21 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_transaction_history_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction_history',
            name='method',
            field=models.CharField(default='None', max_length=100),
        ),
    ]