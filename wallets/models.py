from django.db import models
from accounts.models import account

class BranchAccounts(models.Model):
    main_account    = models.ForeignKey(account, on_delete=models.SET_NULL, null=True, blank=True)
    total_balance   = models.DecimalField(decimal_places=2, max_digits=10, null=True, default=0)
    add_money       = models.DecimalField(decimal_places=1, max_digits=10, null=True, blank=True)
    take_money      = models.DecimalField(decimal_places=1, max_digits=10, null=True, blank=True)
    currency        = models.CharField(max_length=6, null=True)

    def __str__(self):
        return f'Username : {self.main_account.created_by}, Currency : {self.currency}'
