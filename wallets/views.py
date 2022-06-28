import os, json, requests, decimal, stripe

from django.db.models import F
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.translation import gettext as _
from django.conf import settings

from .models import BranchAccounts
from .forms import BankInfo
from users.functions import CountryDict
from accounts.models import Account, CustomUser, AccountInterest, TransactionHistory
from accounts.functions import correct_user, get_currency_symbol, currency_min

with open("/etc/config.json") as config_file:
    config = json.load(config_file)

@login_required
def WalletSearch(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()

    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/country_currencies_clean.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)
    
    all_currencies = data.items()

    context = {
        "pk" : pk,
        "data" : data,
        "all_currencies" : all_currencies,
    }
    return render(request, "wallets/wallet_search.html", context)


@login_required
def NewWallet(request, pk, currency):
    if not correct_user(pk):
        raise PermissionDenied()

    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/country_currencies_clean.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)
    
    # checking if user selected/entered a correct wallet name
    for i in data:
        if currency not in data[i]:
            kick = True
        elif currency == Account.objects.get(pk=pk).main_currency:
            messages.warning(request, _("You cannot make a wallet with the same currency as your main account !"))
            return redirect('accounts:home', pk=pk)
        else:
            kick = False
            break
        
    if kick is False:
        branch_accounts = BranchAccounts.objects.filter(main_account__pk=pk)
        if branch_accounts.count() >= 10:
            messages.warning(request, _("You already have the maximum number of wallets !"))
        else:
            if request.method == "POST":
                for wallet in branch_accounts:
                    if wallet.currency == currency:
                        messages.warning(request, _("You already have that wallet !"))
                        return redirect('accounts:home', pk=pk)

                main_account = Account.objects.get(pk=pk)
                BranchAccounts.objects.create(main_account=main_account, currency=currency)

                # success message
                messages.success(request, _(f"You have successfully added {currency} as one of your wallets !"))
                return redirect('accounts:home', pk=pk)

        context = {
            "pk" : pk,
            "currency" : currency,
            "wallets" : branch_accounts,
        }
        return render(request, "wallets/new_wallet.html", context)
    else:
        messages.warning(request, _("That is not a valid wallet name !"))
        return redirect('accounts:home', pk=pk)


@login_required
def CurrencyExchange(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()

    # getting user's currency stuff
    User                = CustomUser.objects.get(pk=request.user.pk)

    # redirecting to new card if user doesn't have a card
    if User.stripe_id is None:
        return redirect("wallets:new-card", pk=pk)

    currency_name       = User.currency
    currency_symbol_    = get_currency_symbol(currency_name)
    currency_min_       = currency_min(currency_name)
    currency_options    = [(currency_name, currency_symbol_, currency_min_)]


    branch_acc = BranchAccounts.objects.filter(main_account__pk=pk)
    for wallet in branch_acc:
        currency_options.append((wallet.currency, get_currency_symbol(wallet.currency), currency_min(wallet.currency)))
    
    context = {
        "pk"                    : pk,
        "currency_options"      : currency_options,
        "currency"              : currency_name,
        "user_currency_symbol"  : currency_symbol_,
    }
    return render(request, "wallets/currency_exchange.html", context)


@login_required
def CurrencyExchangeConfirm(request, pk, from_, amount, to):
    if not correct_user(pk):
        raise PermissionDenied()

    User                = CustomUser.objects.get(pk=request.user.pk)
    # redirecting to new card if user doesn't have a card
    if User.stripe_id is None:
        return redirect("wallets:new-card", pk=pk)

    wallet          = BranchAccounts.objects.filter(main_account__pk=pk)
    acc_interest    = AccountInterest.objects.get(pk=pk)
    acc             = Account.objects.get(pk=pk)
    min_to          = currency_min(to)
    min_from        = currency_min(from_)
    acc_currency    = currency_min(acc.main_currency)
    notEnough = False

    # confirming from and to currencies
    if min_to is None or min_from is None: # the currency doesnt exist (JXL)
        messages.warning(request, _("You cannot exchange with the specified currencies !"))
        return redirect('accounts:home', pk=pk)
    elif from_ == to: # exchanging the same currencies
        messages.warning(request, _("You cannot exchange the same currencies !"))
        return redirect('accounts:home', pk=pk)
    elif not wallet.filter(currency=to).exists() and acc.main_currency != to:
        messages.warning(request, _("You do not own the specified wallets !"))
        return redirect('accounts:home', pk=pk)
    elif not wallet.filter(currency=from_).exists() and acc.main_currency != from_:
        messages.warning(request, _("You do not own the specified wallets !"))
        return redirect('accounts:home', pk=pk)
    
    # confirming the amount is a number and is within the min range
    if amount.replace('.','',1).isdigit():
        if float(amount) < float(min_from):
            messages.warning(request, _("You have chosen a value below the minimum amount to exchange !"))
            return redirect('wallets:currency-exchange', pk=pk)
    else:
        return redirect('wallets:currency-exchange', pk=pk)

    # if user has enough money
    if from_ == acc.main_currency:
        if float(acc.total_balance) < float(amount):
            notEnough = True
    else:
        for wallet in wallet.filter(currency=from_):
            if float(wallet.total_balance) < float(amount):
                notEnough = True
    if notEnough:
        messages.warning(request, _("You do not have enough money for this transaction !"))
        return redirect('wallets:currency-exchange', pk=pk)

    # getting the up to date rate
    url = f'https://api.exchangerate.host/convert?from={from_}&to={to}'
    response = requests.get(url) # getting a response
    data = response.json() # getting the data
    ex_rate = round(decimal.Decimal(data['result']), 4)

    # idk why django gives an error without this line smh
    wallet = BranchAccounts.objects.filter(main_account__pk=pk)

    if request.method == "POST":
        # sending to a wallet
        if wallet.filter(currency=to): 

            # subtracting the money from the user's wallet
            acc.total_balance = F('total_balance') - float(amount)
            acc.save()

            # adding the money to the user's wallet
            wallet.filter(currency=to).update(total_balance = F('total_balance') + float(amount) * float(ex_rate))
            
            # updating user's interest_account
            acc_interest.interest = F('interest') - float(amount)
            acc_interest.save()

            # sending from account to wallet
            if from_ == CustomUser.objects.get(pk=pk).currency:
                history = TransactionHistory(
                    person=acc, 
                    second_wallet=wallet.get(currency=to), 
                    price=float(amount), 
                    ex_rate=ex_rate, 
                    exchanged_price=float(amount) * float(ex_rate), 
                    method="Exchange"
                )
            # sending from another wallet to wallet
            else:
                history = TransactionHistory(
                    wallet=wallet.get(currency=from_), 
                    second_wallet=wallet.get(currency=to), 
                    price=float(amount), 
                    ex_rate=ex_rate, 
                    exchanged_price=float(amount) * float(ex_rate), 
                    method="Exchange"
                )
            # saving this transaction to history
            history.save()

            # success msg & redirect
            messages.success(request, _("You have successfuly exchanged your desired currencies !"))
            return redirect("accounts:home", pk=pk)
        
        # sending to an account
        elif acc.main_currency == to: 
            # subtracting the money from the user's wallet
            wallet.filter(currency=from_).update(total_balance = F('total_balance') - float(amount))

            # adding the money to the user's account
            acc.total_balance = F('total_balance') + float(amount) * float(ex_rate)
            acc.save()

            # updating user's interest_account
            acc_interest.interest = F('interest') + float(amount) * float(ex_rate)
            acc_interest.save()

            # saving this transaction to history
            history = TransactionHistory(
                wallet=wallet.get(currency=from_), 
                second_person=acc, 
                price=float(amount), 
                ex_rate=ex_rate, 
                exchanged_price=float(amount) * float(ex_rate), 
                method="Exchange"
            )
            history.save()

            # msg & redirect
            messages.success(request, _("You have successfuly exchanged your desired currencies !"))
            return redirect("accounts:home", pk=pk)
        else:
            messages.warning(request, _("You do not have a wallet with the specified currency !"))
            return redirect("wallets:wallet-search", pk=pk)

    context = {
        "from"          : from_,
        "from_symbol"   : get_currency_symbol(from_),
        "to"            : to,
        "to_symbol"     : get_currency_symbol(to),
        "amount"        : amount,
        "ex_rate"       : ex_rate,
    }
    return render(request, "wallets/currency_exchange_confirm.html", context)


@login_required
def Card_or_Bank(request, pk):
    return render(request, "wallets/card_or_bank.html", {"pk" : pk})


@login_required
def Bank(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()

    user = CustomUser.objects.get(pk=pk)
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
#         'clientId': "6235305af410cd001a443813",
#         'secret': "f09ba69583a6d19be07bf9df42a7d1",
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