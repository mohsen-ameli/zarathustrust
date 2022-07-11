from django.contrib import admin
from . import models

class detailsAdmin(admin.ModelAdmin):
    model = models.Account

    fields=(('created_by', 'primary'), ('currency', 'iso2'), 'total_balance', ('add_money', 'take_money'), 'bonus')


class detailsTransactions(admin.ModelAdmin):
    model = models.TransactionHistory

    fields = (
        'person', 
        'second_person',
        ('price', 'ex_rate', 'exchanged_price'), 
        'purpose_of_use', 
        'method'
    )


admin.site.register(models.Account, detailsAdmin)
admin.site.register(models.AccountInterest)
admin.site.register(models.TransactionHistory, detailsTransactions)
