# Generated by Django 3.2.13 on 2022-07-03 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_customuser_iso2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=255, unique=True, verbose_name='email address'),
        ),
    ]
