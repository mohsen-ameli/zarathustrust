# Generated by Django 3.2.12 on 2022-02-12 23:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0001_initial'),
        ('accounts', '0034_delete_branchaccounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction_history',
            name='second_wallet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='second_wallet', to='wallets.branchaccounts'),
        ),
        migrations.AddField(
            model_name='transaction_history',
            name='wallet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wallet', to='wallets.branchaccounts'),
        ),
        migrations.AlterField(
            model_name='transaction_history',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.account'),
        ),
    ]