from django.contrib import admin
from .models import account, account_interest, transaction_history

admin.site.register(account)
admin.site.register(account_interest)
admin.site.register(transaction_history)
