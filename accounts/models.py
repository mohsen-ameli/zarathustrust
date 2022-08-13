from django.db import models
from django.utils.translation import gettext as _
from users.models import CustomUser
from django.db.models import F


class Account(models.Model):
    created_by    = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    total_balance = models.DecimalField(decimal_places=2, max_digits=10, null=True, default=0)
    add_money     = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    take_money    = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    bonus         = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    currency      = models.CharField(max_length=3, null=True)
    iso2          = models.CharField(max_length=2, null=True)
    primary       = models.BooleanField(null=True)

    def saveView(self, *args, **kwargs):
        if self.primary:
            try:
                accountInterest = AccountInterest.objects.get(pk=self.pk)
            except:
                pass

        if self.add_money:
            # updating AccountInterest
            if self.primary:
                accountInterest.interest = F("interest") + self.add_money
                accountInterest.save()

            # updating self
            self.total_balance = self.total_balance + self.add_money
            
            self.add_money = 0
        elif self.take_money:
            # updating AccountInterest
            if self.primary:
                accountInterest.interest = F("interest") - self.take_money
                accountInterest.save()

            # updating self
            self.total_balance = self.total_balance - self.take_money

            self.take_money = 0
        if not kwargs.get('inside'):
            super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.add_money:
            # updating transaction
            transaction = TransactionHistory(person=self, method="Deposit", price=self.add_money)
            transaction.save()
        elif self.take_money:
            # updating transaction
            transaction = TransactionHistory(person=self, method="Withdraw", price=self.take_money)
            transaction.save()

        self.saveView(self, inside=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Username: {self.created_by.username}, Currency: {self.currency}, Primary: {self.primary}'


class AccountInterest(models.Model):
    interest                    = models.DecimalField(decimal_places=10, max_digits=30, null=True)
    interest_rate               = models.DecimalField(decimal_places=20, max_digits=30, null=True, default=0)

    def __str__(self):
        return f'account-pk : {self.pk}'


class TransactionHistory(models.Model):
    person              = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    second_person       = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="second_person")
    date                = models.DateTimeField(auto_now_add=True)
    price               = models.DecimalField(decimal_places=2, max_digits=10)
    purpose_of_use      = models.CharField(max_length=500, null=True, blank=True)
    method              = models.CharField(max_length=100, default="None")
    ex_rate             = models.DecimalField(decimal_places=4, max_digits=10, null=True, blank=True)
    exchanged_price     = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)

    def message(self):
        if not self.purpose_of_use:
            return
        return ''.join(self.purpose_of_use)

    def __str__(self):
        price = round(self.price)

        try:
            person = self.person.created_by.username
        except AttributeError:
            person = "Anonymous"
        try:
            second_person = self.second_person.created_by.username
        except AttributeError:
            second_person = "Anonymous"
        
        if not self.person:
            try:
                person = self.wallet.main_account.created_by.username
            except:
                person = "Anonymous"
        
        if self.method == "Transfer":
            return f'TRANSFER from {person} to {second_person} for the amount {price} at {self.date}'
        elif self.method == "Payment":
            return f'PAYMENT from {person} to {second_person} for the amount {price} at {self.date}'
        elif self.method == "Deposit":
            return f'DEPOSIT from {person} for the amount {self.price} at {self.date}'
        elif self.method == "Withdraw":
            return f'WITHDRAW from {person} for the amount {self.price} at {self.date}'
        elif self.method == "Cash Out":
            return f'CASH OUT as {person} for the amount {self.price} at {self.date}'
        elif self.method == "Exchange":
            return f'EXCHANGE as {person} for the amount {self.price} at {self.date}'
