from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, code
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
                    'phone_ext',
                    'phone_number',
                    'iban',
                    'is_business'
                )
            }
        )
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(code)