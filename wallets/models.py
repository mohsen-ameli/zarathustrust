from django.db import models
from accounts.models import transaction_history

class BranchAccounts(models.Model):
    main_account    = models.ForeignKey("accounts.account", on_delete=models.SET_NULL, null=True, blank=True)
    total_balance   = models.DecimalField(decimal_places=2, max_digits=10, null=True, default=0)
    add_money       = models.DecimalField(decimal_places=1, max_digits=10, null=True, blank=True)
    take_money      = models.DecimalField(decimal_places=1, max_digits=10, null=True, blank=True)
    currency        = models.CharField(max_length=6, null=True)
    iso2            = models.CharField(max_length=2, null=True)

    def save(self, *args, **kwargs):
        if self.add_money:
            self.total_balance = self.total_balance + self.add_money
            
            r = transaction_history(wallet=self, method="Deposit", price=self.add_money)
            r.save()

            self.add_money = 0
        elif self.take_money:
            r = transaction_history(wallet=self, method="Withdraw", price=self.take_money)
            r.save()

            self.take_money = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Username : {self.main_account.created_by}, Currency : {self.currency}'
