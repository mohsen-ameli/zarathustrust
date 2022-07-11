from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields import BooleanField, CharField, PositiveIntegerField
from django.contrib.auth.validators import UnicodeUsernameValidator
import random
from django_countries.fields import CountryField


class MyValidator(UnicodeUsernameValidator):
    regex = r'^[\w.@+\- ]+$'

class CustomUser(AbstractUser):
    username_validator = MyValidator()
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 5-15 characters allowed. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
            error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    country             = CountryField(null=True)
    currency            = CharField(max_length=3, null=True)
    iso2                = CharField(max_length=2, null=True)
    language            = CharField(max_length=15, null=True)
    phone_ext           = CharField(max_length=3, null=True)
    phone_number        = CharField(max_length=20, null=True)
    # iban                = CharField(max_length=30, null=True, blank=True)
    bank_account_number = CharField(max_length=50, null=True, blank=True)
    referral_code       = CharField(max_length=12, null=True)

    is_business         = BooleanField(null=True, blank=True, default=False)
    # type_business       = CharField(max_length=10, null=True)
    # business_website    = CharField(max_length=30, null=True)

    def __str__(self):
        return f'{self.username}, pk: {self.pk}'

    def get_currency(self):
        return self.currency


CustomUser._meta.get_field('username').max_length = 15


class Code(models.Model):
    user                = CharField(max_length=15, null=True)
    email_verify_code   = PositiveIntegerField(blank=True)
    phone_verify_code   = PositiveIntegerField(blank=True)
    iban_verify_code    = CharField(max_length=5, blank=True, null=True)

    def save(self, *args, **kwargs):
        n = 6
        self.email_verify_code = random.randint(10**(n-1),10**n-1)
        self.phone_verify_code = random.randint(10**(n-1),10**n-1)
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
