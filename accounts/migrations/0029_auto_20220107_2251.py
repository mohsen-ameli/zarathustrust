# Generated by Django 3.2.10 on 2022-01-08 03:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_auto_20220107_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction_history',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.account'),
        ),
        migrations.AlterField(
            model_name='transaction_history',
            name='second_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='second_person', to='accounts.account'),
        ),
    ]
