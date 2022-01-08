from django.contrib import admin
from .models import account, account_interest, transaction_history
from users.models import CustomUser

class detailsAdmin(admin.ModelAdmin):
    model = account

    fields=('created_by',  'total_balance', ('add_money', 'take_money'), 'bonus')


admin.site.register(account, detailsAdmin)
admin.site.register(account_interest)
admin.site.register(transaction_history)
