import json, requests, stripe

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.translation import gettext as _
from django.conf import settings

from ..wallets.forms import BankInfo
from accounts.models import CustomUser
from accounts.functions import correct_user

# with open("/etc/config.json") as config_file:
#     config = json.load(config_file)


@login_required
def Card_or_Bank(request, pk):
    return render(request, "wallets/card_or_bank.html", {"pk" : pk})


@login_required
def Bank(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()

    form = BankInfo(request.POST or None)
    if form.is_valid():
        bank_num = request.POST['bank']

    if request.is_ajax():
        print(request.POST.get("AccountId"), request.POST.get("providerId"))

    # getting a token for the user
    url = "https://sandbox.api.yodlee.com/ysl/auth/token"

    clientId = config.get('YODLEE_CLIENT_ID')
    secret = config.get('YODLEE_SECRET')
    loginName = config.get('YODLEE_LOGIN_NAME')

    payload=f'clientId={clientId}&secret={secret}'
    headers = {
        'Api-Version': '1.1',
        'loginName': loginName,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    js = response.json()
    token = js['token']['accessToken']

    context = {
        "form" : form,
        "token" : token
    }
    return render(request, "wallets/bank.html", context)


@login_required
def Card(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()
        
    stripe.api_key = settings.STRIPE_SECRET_KEY
    user = CustomUser.objects.get(pk=pk)

    if request.method == "POST":
        if user.stripe_id is None:
            try:
                # Create a Customer:
                customer = stripe.Customer.create(
                    name=user.username,
                    source=request.POST['stripeToken'],
                    email=user.email,
                    phone=user.phone_number
                )
            except:
                messages.warning(request, _("It seems that your card has declined."))
            # transfer = stripe.Transfer.create(
            #     amount=1,
            #     currency='cad',
            #     description="123123123123",
            #     destination=customer
            # )

            # saving their card id
            user.stripe_id = customer.id
            user.save()
            messages.success(request, _("You have successfuly added your card"))
            return redirect("accounts:home", pk=pk)
        else:
            messages.warning(request, _("You have already attached a card to your account. If you wish to change it, please email our support team."))

    context = {
        "stripe_key" : settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, "wallets/card.html", context)

# stripe.api_key = settings.STRIPE_SECRET_KEY

# configuration = plaid.Configuration(
#     host=plaid.Environment.Sandbox,
#     api_key={
#         'clientId': "",
#         'secret': "",
#     }
# )

# api_client = plaid.ApiClient(configuration)
# client = plaid_api.PlaidApi(api_client)
# try:
#     request = LinkTokenCreateRequest(
#     products=products,
#     client_name="Plaid Quickstart",
#     country_codes=list(map(lambda x: CountryCode(x), ['US', 'CA'])),
#     language='en',
#     user=LinkTokenCreateRequestUser(
#         client_user_id=str(time.time())
#     )
#     )

#     # create link token
#     response = client.link_token_create(request)
#     print(response.to_dict())
# except plaid.ApiException as e:
#     return json.loads(e.body)




# forms.py
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




# card.html
# {% extends "accounts/base.html" %}
# {% load i18n %}
# {% load static %}
# {% block content %}
# <link rel="stylesheet" href="{% static 'wallets/css/card.css' %}">
# <script src="https://js.stripe.com/v3/"></script>

# <div class="card text-white zarathus-card mx-auto">
#     <div class="card-body">
        
#         <form action="{% url 'wallets:new-card' pk=user.pk %}" method="post" id="payment-form">
#             {% csrf_token %}
#             <div class="form-row">
#                 <div class="d-flex">
#                     <label for="card-element">
#                         {% trans "Credit or debit card" %}
#                     </label> 
#                     <img src="{% static 'accounts/images/Powered by Stripe - black.svg' %}" alt="" class="ms-3" style="width: auto; height:2rem;">
#                 </div>
#                 <div class="mt-2" id="card-element">
#                     <!-- A Stripe Element will be inserted here. -->
#                 </div>
            
#                 <!-- Used to display Element errors. -->
#                 <div id="card-errors" role="alert"></div>
#             </div>
#             <p class="text-small pt-2">{% trans "Please note that you will not be able to change this card unless you contact our support team." %}</p>
          
#             <button type="submit" class="neon-button mb-2">{% trans "Add Card" %}</button>
#         </form>


#     </div>
# </div>

# {{ stripe_key|json_script:"stripe_key" }}
# <script src="{% static 'wallets/js/card.js' %}"></script>


# {% endblock content %}










# card_or_bank.html
# {% extends "accounts/base.html" %}
# {% load i18n %}
# {% load crispy_forms_tags %}
# {% block content %}
# <div class="d-lg-flex">
#     <div class="p-3 mx-auto">
#         <div class="card text-white text-center zarathus-card" style="height: 20rem;">
#             <div class="card-body" style="display: flex; flex-direction: column;">
#                 <h3 class="fw-normal">
#                     {% trans "Link a Card" %}
#                     <hr class="zarathus-hr">
#                 </h3>
#                 <h5 class="fw-normal">{% trans "Link a debit or credit card. This will be the easiest way to interact with your money on the website. We will ensure your card's safety by using Stripe to store your information." %}</h5>
#                 <div class="mt-auto">
#                     <hr class="zarathus-hr">
#                     <a class="neon-button-green fixed-bottom" href="{% url 'wallets:new-card' pk=pk %}">{% trans "New Card" %}</a>
#                 </div>
#             </div>
#         </div>
#     </div>
    
#     <div class="p-3 mx-auto">
#         <div class="card text-white text-center zarathus-card" style="height: 20rem;">
#             <div class="card-body" style="display: flex; flex-direction: column;">
#                 <h3 class="fw-normal">
#                     {% trans "Link a Bank" %}
#                     <hr class="zarathus-hr">
#                 </h3>
#                 <h5 class="fw-normal">{% trans "Link your bank account by providing the banking account number and depending on your country, your transit number and other information." %}</h5>
#                 <div class="mt-auto">
#                     <hr class="zarathus-hr">
#                     <a class="neon-button-green fixed-bottom" href="{% url 'wallets:new-bank' pk=pk %}">{% trans "New Bank" %}</a>
#                 </div>
#             </div>
#         </div>
#     </div>
# </div>
# {% endblock content %}








# bank.html
# {% extends "accounts/base.html" %}
# {% load i18n %}
# {% load static %}
# {% load crispy_forms_tags %}
# {% block content %}
# <script type='text/javascript' src='https://cdn.yodlee.com/fastlink/v4/initialize.js'></script>

# <div id="container-fastlink"></div>

# {% csrf_token %}

# <script>
#     (function (window) {
#         const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
#         var pk = "{{ user.pk }}"
#         var token = "{{ token }}"
#         var fastlinkBtn = document.getElementById('btn-fastlink');
#         function huh() {
#             window.fastlink.open({
#                 fastLinkURL: 'https://fl4.sandbox.yodlee.com/authenticate/restserver/fastlink',
#                 accessToken: `Bearer ${token}`,
#                 amplitude_account: "",
#                 params: {
#                     configName : 'Verification'
#                 },
#                 onSuccess: function (data) {
#                     // will be called on success. For list of possible message, refer to onSuccess(data) Method.
#                     $.ajax({
#                         type: 'POST',
#                         url:`new_bank`,
#                         data : {
#                             'csrfmiddlewaretoken':csrftoken,
#                             'AccountId' : data.providerAccountId,
#                             'providerId' : data.providerId
#                         },
#                     })
#                     console.log(data.providerAccountId);
#                     console.log(data.providerId);
#                 },
#                 onError: function (data) {
#                 // will be called on error. For list of possible message, refer to onError(data) Method.
#                 },
#                 onClose: function (data) {
#                 // will be called called to close FastLink. For list of possible message, refer to onClose(data) Method.
#                 },
#                 onEvent: function (data) {
#                 // will be called on intermittent status update.
#                 }
#             },
#             'container-fastlink');
#         };huh();
#     }(window));
# </script>


# <!-- <link rel="stylesheet" href="{% static 'wallets/css/card.css' %}">
# <script src="https://js.stripe.com/v3/"></script>

# <div class="card text-white zarathus-card mx-auto">
#     <div class="card-body">
        
#         <form action="{% url 'wallets:new-bank' pk=user.pk %}" method="post" id="payment-form" autocomplete="off">
#             {% csrf_token %}
#             <h3 class="fw-normal text-center">{% trans "Enter your bank information" %}</h3>
#             <hr class="zarathus-hr">

#             {% crispy form %}

#             <button type="submit" class="neon-button mb-2">{% trans "Add Bank" %}</button>
#         </form>


#     </div>
# </div> -->
# {% endblock content %}