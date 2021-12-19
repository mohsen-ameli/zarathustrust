from django import forms
from django.forms import ModelForm
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

class TransferForm(ModelForm):
    money_to_send  = forms.DecimalField(label=_('Enter Amount'),
        widget     = forms.TextInput(attrs={'placeholder': '$0.0'}))
    # account      = forms.ModelChoiceField(queryset=account.objects.all() ,label='Choose Account')
    target_account = forms.CharField(max_length=30, label=_('Enter Account'),
        widget     = forms.TextInput(attrs={'placeholder': 'username, email, phone number (+1999999999)'}))
    purpose        = forms.CharField(max_length=500, required=False, label=_('purpose of use (optional)'),
        widget     = forms.TextInput(attrs={'placeholder': _('e.g. Happy Birthday honey !')}))

    class Meta:
        model  = account
        fields = ['target_account', 'money_to_send']