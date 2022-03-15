from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ReferralCode
from .forms import UserRegisterForm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = UserRegisterForm

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'User Info',
            {
                'fields': (
                    'country',
                    'language',
                    'currency',
                    'phone_ext',
                    'phone_number',
                    'is_business',
                )
            }
        )
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ReferralCode)