# Generated by Django 2.2 on 2021-06-08 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20210608_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_business',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
