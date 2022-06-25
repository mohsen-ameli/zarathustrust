from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Account
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class AddMoneyForm(forms.ModelForm):
    add_money  = forms.DecimalField(label=_('Enter Amount'),
        widget = forms.TextInput(attrs={'placeholder': '$0.0'}))

    class Meta:
        model  = Account
        fields = ['add_money']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            FloatingField("add_money"),
        )


class TakeMoneyForm(forms.ModelForm):
    take_money = forms.DecimalField(label=_('Enter Amount'), 
        widget = forms.TextInput(attrs={'placeholder': '$0.0'}))

    class Meta:
        model = Account
        fields = ['take_money']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            FloatingField("take_money"),
        )


class TransferSendForm(forms.ModelForm):
    money_to_send  = forms.DecimalField(label=_('Amount to Send'),
        widget     = forms.TextInput(attrs={'placeholder': '$0.0'}))
    purpose        = forms.CharField(max_length=200, required=False, label=_('Message (optional)'),
            widget     = forms.TextInput(attrs={'placeholder': _('e.g. Happy Birthday Honey !')}))

    class Meta:
        model  = Account
        fields = ['money_to_send', 'money_to_send']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            FloatingField("money_to_send"),
            FloatingField("purpose"),
        )


# class SettingsForm(forms.ModelForm):
    
#     class Meta:
#         model = CustomUser
