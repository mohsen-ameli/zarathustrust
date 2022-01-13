from django.contrib import admin
from django.db.models import fields
from . import models
from users.models import CustomUser

class detailsAdmin(admin.ModelAdmin):
    model = models.account

    fields=('created_by', 'main_currency', 'total_balance', ('add_money', 'take_money'), 'bonus')


class detailsTransactions(admin.ModelAdmin):
    model = models.transaction_history

    fields = ('person', 'second_person', ('price', 'ex_rate', 'ex_price'), 'purpose_of_use', 'method')


admin.site.register(models.account, detailsAdmin)
admin.site.register(models.BranchAccounts)
admin.site.register(models.account_interest)
admin.site.register(models.transaction_history, detailsTransactions)
