from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.db.models.deletion import CASCADE
from django.db.models.fields import BooleanField, CharField, PositiveIntegerField
import random
import string
from django_countries.fields import CountryField


class CustomUser(AbstractUser):
    country             = CountryField(null=True)
    currency            = CharField(max_length=6, null=True)
    language            = CharField(max_length=15, null=True)
    phone_ext           = CharField(max_length=4, null=True, blank=True)
    phone_number        = CharField(max_length=20, null=True)
    iban                = CharField(max_length=30, null=True, blank=True)

    is_business         = BooleanField(null=True, blank=True, default=False)
    type_business       = CharField(max_length=10, null=True)
    business_website    = CharField(max_length=30, null=True)

    def __str__(self):
        return f'{self.username}, pk: {self.pk}'


CustomUser._meta.get_field('username').max_length = 15
CustomUser._meta.get_field('username').help_text = _(
    'Required. 5-15 characters allowed. Letters, digits and @/./+/-/_ only.'
)



class code(models.Model):
    user                = CharField(max_length=15, null=True)
    email_verify_code   = PositiveIntegerField(blank=True)
    phone_verify_code   = PositiveIntegerField(blank=True)
    iban_verify_code    = CharField(max_length=5, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Email & phone number verificaiton
        for e in range(2):
            number_list = [x for x in range(10)]
            code_items = []

            for i in range(6):
                num = random.choice(number_list)
                code_items.append(num)

            code_string = "".join(str(item) for item in code_items)
            if e == 1:
                self.email_verify_code = code_string
            else:
                self.phone_verify_code = code_string
        # End

        # IBAN verificaiton
        code_items = []

        for i in range(1):
            num = round(random.uniform(0.01, 0.50), 2)
            code_items.append(num)

        code_string = "".join(str(item) for item in code_items)
        self.iban_verify_code = code_string
        # End

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user}'


class ReferralCode(models.Model):
    user                = models.OneToOneField(CustomUser, on_delete=CASCADE)
    referral_code       = CharField(max_length=12, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Referral Code
        code_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        self.referral_code = code_string
        # End
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user}'
