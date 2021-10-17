from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django.db.models.deletion import CASCADE
from django.db.models.fields import BooleanField, CharField
import random
import string

class CustomUser(AbstractUser):
    phone_ext           = CharField(max_length=4, null=True, blank=True)
    phone_number        = CharField(max_length=20, null=True)
    iban                = CharField(max_length=30, null=True, blank=True)

    is_business         = BooleanField(null=True, blank=True, default=False)
    type_business       = CharField(max_length=10, null=True)
    business_website    = CharField(max_length=30, null=True)

    def __str__(self):
        return f'{self.username}, pk: {self.pk}'

class code(models.Model):
    user                = models.OneToOneField(CustomUser, on_delete=CASCADE)
    email_verify_code   = models.PositiveIntegerField(blank=True)
    phone_verify_code   = models.PositiveIntegerField(blank=True)
    iban_verify_code    = models.CharField(max_length=5, blank=True, null=True)
    referral_code       = models.CharField(max_length=12, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Email & phone number verificaiton
        for e in range(2):
            number_list = [x for x in range(10)]
            code_items = []

            for i in range(5):
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

        # Referral Code
        code_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        self.referral_code = code_string
        # End

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user}'
