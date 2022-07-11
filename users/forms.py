from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(help_text="We will not share your email with anyone.")
    phone_number = forms.CharField(
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(attrs={"placeholder": "999-999-9999"}),
    )

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()

        # checking to see if username has at least 5 characters
        username = cleaned_data.get('username')
        if username and len(username) < 5:
            self.add_error('username', "Please choose a username with at least 5 characters.")

        return cleaned_data


    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "phone_number",
            "password1",
            "password2",
        ]


# class BusinessForm(UserCreationForm):
#     biz_types = [
#         ("1", "Sole Proprietorship"),
#         ("2", "Partnership"),
#         ("3", "Corporation"),
#         ("4", "Limited Liability Company"),
#     ]

#     type_business = forms.ChoiceField(choices=biz_types)
#     business_website = forms.CharField(max_length=30)

#     class Meta:
#         model = CustomUser
#         fields = [
#             "username",
#             "email",
#             "phone_ext",
#             "phone_number",
#             "iban",
#             "password1",
#             "password2",
#             "type_business",
#             "business_website",
#         ]