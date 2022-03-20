from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_bootstrap5.bootstrap5 import FloatingField

class BankInfo(forms.Form):
    bank = forms.CharField(max_length=20, label=_('Bank Account Number (IBAN)'), help_text=_("We will use Stripe to verify your bank account."))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            FloatingField("bank"),
        )
