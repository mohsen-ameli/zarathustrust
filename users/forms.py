import phonenumbers

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from .models import CustomUser, code

# iban = forms.CharField(
#     max_length=30,
#     label=_("IBAN (optional)"),
#     required=False,
#     help_text=_("For European countries only !"),
# )
# country_choices = [
#     ("1", "🇨🇦(+1)"),
#     ("1", "🇺🇸(+1)"),
#     ("49", "🇩🇪(+49)"),
#     ("98", "🇮🇷(+98)"),
# ]
# country = CountryField(blank=True)

# class PhoneEnterForm(forms.ModelForm):
#     phone_number = forms.CharField(
#         max_length=20,
#         label="",
#         widget=forms.TextInput(attrs={"placeholder": "999-999-9999"}),
#     )

#     class Meta:
#         model = CustomUser
#         fields = ['phone_number']


# class CountryForm(forms.ModelForm):
#     country = forms.ChoiceField(choices=countries)

#     class Meta:
#         model = CustomUser
#         fields = ['country']

# class CountryForm(forms.ModelForm):
#     country_choices = [
#         ("1", "🇨🇦(+1)"),
#         ("1", "🇺🇸(+1)"),
#         ("49", "🇩🇪(+49)"),
#         ("98", "🇮🇷(+98)"),
#     ]

#     # country = CountryField(blank=True)

#     country = forms.ChoiceField(
#         choices=country_choices,
#         label="Country")

#     class Meta:
#         model = CountryChoose
#         fields = ['country']


class RegisterForm(UserCreationForm):
    email = forms.EmailField(help_text=_("We will not share your email with anyone."))
    phone_number = forms.CharField(
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(attrs={"placeholder": "999-999-9999"}),
    )

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()

        # checking to see if username has at least 5 characters
        username = cleaned_data.get('username')
        if len(username) < 5:
            self.add_error('username', _("Please choose a username with at least 5 characters."))

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

    # def __init__(self, *args, **kwargs):
    #     super(RegisterForm, self).__init__(*args, **kwargs)
    #     self.fields['username'].widget.attrs['min'] = 5



class BusinessForm(UserCreationForm):
    biz_types = [
        ("1", "Sole Proprietorship"),
        ("2", "Partnership"),
        ("3", "Corporation"),
        ("4", "Limited Liability Company"),
    ]

    type_business = forms.ChoiceField(choices=biz_types)
    business_website = forms.CharField(max_length=30)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "phone_ext",
            "phone_number",
            "iban",
            "password1",
            "password2",
            "type_business",
            "business_website",
        ]


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = "__all__"


class EmailCodeForm(forms.ModelForm):
    email_verify_code = forms.CharField(
        label=_("Code"), help_text=_("Please enter the email verification code")
    )

    class Meta:
        model = code
        fields = ["email_verify_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            FloatingField("email_verify_code"),
        )


class PhoneCodeForm(forms.ModelForm):
    phone_verify_code = forms.CharField(
        label=_("Code"), help_text=_("Please enter the phone number verification code")
    )

    class Meta:
        model = code
        fields = ["phone_verify_code"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            FloatingField("phone_verify_code"),
        )


class IbanCodeForm(forms.ModelForm):
    iban_verify_code = forms.CharField(
        label=_("Code"), help_text=_("Please enter the iban verification code")
    )

    class Meta:
        model = code
        fields = ["iban_verify_code"]


class ReferralCodeForm(forms.ModelForm):
    referral_code = forms.CharField(
        required=False,
        label=_("Referral Code(Optional)"),
        help_text=_(
            "Please enter your referral code to get grand prizes , or leave blank for no prize !"
        ),
    )

    class Meta:
        model = code
        fields = ["referral_code"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            FloatingField("referral_code"),
        )
