# Generated by Django 2.2 on 2021-06-08 22:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_customuser_business'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='business',
            new_name='is_business',
        ),
    ]
