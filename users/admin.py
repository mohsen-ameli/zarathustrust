from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'User Info',
            {
                'fields': (
                    'country',
                    'language',
                    ('currency', 'iso2'),
                    'phone_ext',
                    'phone_number',
                    'is_business',
                    'referral_code',
                    'bank_account_number'
                )
            }
        )
    )

admin.site.register(CustomUser, CustomUserAdmin)