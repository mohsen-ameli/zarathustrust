from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _

from .models import CustomUser, code

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
        if username and len(username) < 5:
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


class PhoneCodeForm(forms.ModelForm):
    phone_verify_code = forms.CharField(
        label=_("Code"), help_text=_("Please enter the phone number verification code")
    )

    class Meta:
        model = code
        fields = ["phone_verify_code"]


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