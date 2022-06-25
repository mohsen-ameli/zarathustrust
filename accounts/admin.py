from django.contrib import admin
from . import models

class detailsAdmin(admin.ModelAdmin):
    model = models.Account

    fields=('created_by', ('main_currency', 'iso2'), 'total_balance', ('add_money', 'take_money'), 'bonus')


class detailsTransactions(admin.ModelAdmin):
    model = models.TransactionHistory

    fields = (
        ('person', 'wallet'), 
        ('second_person', 'second_wallet'),
        ('price', 'ex_rate', 'exchanged_price'), 
        'purpose_of_use', 
        'method'
    )


admin.site.register(models.Account, detailsAdmin)
admin.site.register(models.AccountInterest)
admin.site.register(models.TransactionHistory, detailsTransactions)
