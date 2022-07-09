# Generated by Django 3.2.14 on 2022-07-09 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0045_alter_account_money_to_send'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountinterest',
            name='interest_rate',
            field=models.DecimalField(decimal_places=20, default=0, max_digits=30, null=True),
        ),
    ]
