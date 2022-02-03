import os, json

from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.translation import gettext as _

from .models import BranchAccounts
from accounts.models import account
from accounts.functions import correct_user

@login_required
def WalletSearch(request, pk):
    if correct_user(pk):
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
    else:
        raise PermissionDenied


@login_required
def NewWallet(request, pk, currency):
    if correct_user(pk):
        project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file = f'{project}/json/country_currencies_clean.json' # getting the file containing all country codes
        with open(file, 'r') as config_file: # opening and reading the json file
            data = json.load(config_file)
        
        for i in data:
            if currency not in data[i]:
                kick = True
            else:
                kick = False
                break
            
        if kick is False:
            branch_accounts = BranchAccounts.objects.filter(main_account__pk=pk)
            if branch_accounts.count() >= 10:
                messages.warning(request, _(f"You already have the maximum number of wallets !"))
            else:
                if request.method == "POST":
                    for wallet in branch_accounts:
                        if wallet.currency == currency:
                            messages.warning(request, _(f"You already have that wallet !"))
                            return redirect(reverse("accounts:home", kwargs={"pk":pk}))

                    main_account = account.objects.get(pk=pk)
                    BranchAccounts.objects.create(main_account=main_account, currency=currency)

                    # success message
                    messages.success(request, _(f"You have successfully added {currency} as one of your wallets !"))
                    return redirect(reverse("accounts:home", kwargs={"pk":pk}))

            context = {
                "pk" : pk,
                "currency" : currency,
                "wallets" : branch_accounts,
            }
            return render(request, "wallets/new_wallet.html", context)
        else:
            messages.warning(request, _(f"That is not a valid wallet name !"))
            return redirect(reverse("accounts:home", kwargs={"pk":pk}))
    else:
        raise PermissionDenied


@login_required
def CurrencyExchange(request, pk):
    if correct_user(pk):
        context = {
            "pk" : pk,
        }
        return render(request, "wallets/currency_exchange.html", context)
    else:
        raise PermissionDenied