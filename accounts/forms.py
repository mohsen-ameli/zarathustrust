from django import forms
from django.forms import ModelForm, fields
from django.utils.translation import ugettext_lazy as _
from .models import account


class TakeMoneyForm(ModelForm):
    take_money = forms.DecimalField(label=_('Enter Amount'), 
        widget = forms.TextInput(attrs={'placeholder': '$0.0'}))

    class Meta:
        model = account
        fields = ['take_money']


class AddMoneyForm(ModelForm):
    add_money  = forms.DecimalField(label=_('Enter Amount'),
        widget = forms.TextInput(attrs={'placeholder': '$0.0'}))

    class Meta:
        model  = account
        fields = ['add_money']


class PaginationForm(forms.Form):
    pag_num = forms.IntegerField(label="", 
            widget=forms.TextInput(attrs={'placeholder' : _("Enter a number"), 'size': 30}),
            help_text=_('Enter the number "0" to show all transactions'),
            required=False
    )


class TransferSearchForm(forms.ModelForm):
    target_account = forms.CharField(max_length=30, label=_('Reciever'),
        widget     = forms.TextInput(attrs={'placeholder': 'Username or Email or Phone Number'}))

    class Meta:
        model = account
        fields = ["target_account"]


class TransferSendForm(forms.ModelForm):
    money_to_send  = forms.DecimalField(label=_('Amount to Send'),
        widget     = forms.TextInput(attrs={'placeholder': '$0.0'}))
    purpose        = forms.CharField(max_length=500, required=False, label=_('Message (optional)'),
            widget     = forms.TextInput(attrs={'placeholder': _('e.g. Happy Birthday Honey !')}))

    class Meta:
        model  = account
        fields = ['money_to_send', 'money_to_send']
