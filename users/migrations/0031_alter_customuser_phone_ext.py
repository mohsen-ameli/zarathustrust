# Generated by Django 3.2.14 on 2022-07-12 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_alter_customuser_bank_account_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_ext',
            field=models.CharField(max_length=6, null=True),
        ),
    ]
