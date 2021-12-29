# Generated by Django 3.2.7 on 2021-12-25 23:48

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_customuser_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='country',
            field=django_countries.fields.CountryField(max_length=2, null=True),
        ),
    ]