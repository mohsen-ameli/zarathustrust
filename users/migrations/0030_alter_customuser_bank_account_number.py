# Generated by Django 3.2.14 on 2022-07-11 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_auto_20220711_0224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
