# Generated by Django 2.2 on 2021-06-11 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20210608_2200'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='business_website',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='type_business',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
