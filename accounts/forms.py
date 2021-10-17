from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy
from .models import account

class TakeMoneyForm(ModelForm):
    take_money = forms.DecimalField(label=ugettext_lazy('Enter Amount'), 
        widget = forms.TextInput(attrs={'placeholder': '$0.0'}))

    class Meta:
        model = account
        fields = ['take_money']

class AddMoneyForm(ModelForm):
    add_money  = forms.DecimalField(label=ugettext_lazy('Enter Amount'),
        widget = forms.TextInput(attrs={'placeholder': '$0.0'}))

    class Meta:
        model  = account
        fields = ['add_money']

class TransferForm(ModelForm):
    money_to_send  = forms.DecimalField(label=ugettext_lazy('Enter Amount'),
        widget     = forms.TextInput(attrs={'placeholder': '$0.0'}))
    # account      = forms.ModelChoiceField(queryset=account.objects.all() ,label='Choose Account')
    target_account = forms.CharField(max_length=30, label=ugettext_lazy('Enter Account'),
        widget=forms.TextInput(attrs={'placeholder': 'username, email, phone number (+1999999999)'}))

    class Meta:
        model  = account
        fields = ['target_account', 'money_to_send']