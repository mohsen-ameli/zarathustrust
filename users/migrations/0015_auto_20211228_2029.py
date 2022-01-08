# Generated by Django 3.2.10 on 2021-12-29 01:29

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_customuser_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryChoose',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', django_countries.fields.CountryField(max_length=2, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='country',
        ),
    ]