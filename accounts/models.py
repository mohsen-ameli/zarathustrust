import json

from crum import get_current_user
from django.core.mail import send_mail
from django.db import models
from django.db.models.deletion import DO_NOTHING, PROTECT, RESTRICT
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext as _
from users.models import CustomUser
from users.utils import new_user

with open('/etc/config.json') as config_file:
    config = json.load(config_file)


class account(models.Model):
    created_by        = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    total_balance     = models.DecimalField(decimal_places=2, max_digits=10, null=True, default=0)
    add_money         = models.DecimalField(decimal_places=1, max_digits=10, null=True, blank=True)
    take_money        = models.DecimalField(decimal_places=1, max_digits=10, null=True, blank=True)
    bonus             = models.DecimalField(decimal_places=1, max_digits=10, null=True) # remove this default
    target_account    = models.CharField(max_length=30, null=True, blank=True)
    money_to_send     = models.PositiveIntegerField(null=True, default=0)
    main_currency     = models.CharField(max_length=6, null=True)

    def save(self, *args, **kwargs):
        if self.add_money:
            a = account_interest.objects.get(pk=self.pk).interest + self.add_money
            account_interest.objects.filter(pk=self.pk).update(interest=a)
            self.total_balance = self.total_balance + self.add_money

            r = transaction_history(person=self, method="Deposit", price=self.add_money)
            r.save()
            
            self.add_money = 0
        elif self.take_money:
            b = account_interest.objects.get(pk=self.pk).interest - self.take_money
            account_interest.objects.filter(pk=self.pk).update(interest=b)
            self.total_balance = self.total_balance - self.take_money

            r = transaction_history(person=self, method="Withdraw", price=self.take_money)
            r.save()

            self.take_money = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Username : {self.created_by}, Currency : {self.main_currency}'

    def get_absolute_url(self):
        # return '%s/account_profile/' % 18
        return reverse('accounts:account-profile', kwargs={'pk':self.pk})


class account_interest(models.Model):
    interest                    = models.DecimalField(decimal_places=10, max_digits=30, null=True)
    interest_rate               = models.DecimalField(decimal_places=10, max_digits=30, null=True, default=0)

    def __str__(self):
        return f'account-interest-pk : {self.pk}'


class transaction_history(models.Model):
    # prolly dont actually have to have this set as a foreign key
    person              = models.ForeignKey(account, on_delete=models.SET_NULL, null=True)
    second_person       = models.ForeignKey(account, on_delete=models.SET_NULL, null=True, blank=True, related_name="second_person")
    date                = models.DateTimeField(auto_now_add=True)
    price               = models.DecimalField(decimal_places=1, max_digits=10)
    ex_rate             = models.DecimalField(decimal_places=4, max_digits=10, null=True, blank=True, default=0)
    ex_price            = models.DecimalField(decimal_places=1, max_digits=10, null=True, blank=True, default=0)
    purpose_of_use      = models.CharField(max_length=500, null=True, blank=True, default="None")
    method              = models.CharField(max_length=100, default="None")   

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
        if self.method == "Transfer":
            return f'TRANSFER from {person} to {second_person} for the amount ${price} at {self.date}'
        elif self.method == "Payment":
            return f'PAYMENT from {person} to {second_person} for the amount ${price} at {self.date}'
        elif self.method == "Deposit":
            return f'DEPOSIT from {person} for the amount ${self.price} at {self.date}'
        elif self.method == "Withdraw":
            return f'WITHDRAW from {person} for the amount ${self.price} at {self.date}'
        elif self.method == "Cash Out":
            return f'CASH OUT as {person} for the amount ${self.price} at {self.date}'



# signal to create an account_interest, right after an account is created
@receiver(post_save, sender=account)
def account_created_handler(sender, created, instance, *args, **kwargs):
    if created:
        account_interest.objects.create(interest=instance.total_balance, id=instance.pk)

        # Notify us that a new account has been created
        new_user(instance.created_by)

        # Emailing our business users
        EMAIL_ID = config.get('EMAIL_ID')
        id = CustomUser.objects.get(pk=get_current_user().pk).pk
        email = CustomUser.objects.get(pk=get_current_user().pk).email
        if CustomUser.objects.get(pk=id).is_business:
            send_mail(instance.created_by.username,
                        _(f'WHAT UPP'),
                        f'{EMAIL_ID}',
                        [f'{email}'],)


@receiver(pre_delete, sender=account)
def account_delete_hendler(sender, instance, using, *args, **kwargs):
    account_interest.objects.get(id=instance.pk).delete()


@receiver(post_save, sender=account_interest)
def account_interest_created_handler(sender, created, instance, *args, **kwargs):
    if created:
        from .tasks import interest_loop
        interest_loop.delay()
