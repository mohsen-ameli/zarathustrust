# Generated by Django 3.2.14 on 2022-07-11 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_auto_20220711_0221'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='currency',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='iso2',
            field=models.CharField(max_length=2, null=True),
        ),
    ]