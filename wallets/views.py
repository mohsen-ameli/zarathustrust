from email import message
import os, json, requests, decimal

from django.db.models import F
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _

from .models import BranchAccounts
from accounts.models import account, CustomUser
from accounts.functions import correct_user, currency_symbol, currency_min

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
        
        # checking if user selected/entered a correct wallet name
        for i in data:
            if currency not in data[i]:
                kick = True
            elif currency == account.objects.get(pk=pk).main_currency:
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

                    main_account = account.objects.get(pk=pk)
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
    else:
        raise PermissionDenied


@login_required
def CurrencyExchange(request, pk):
    if correct_user(pk):
        # getting user's currency stuff
        User                = CustomUser.objects.get(pk=request.user.pk)
        currency_name       = User.currency
        currency_symbol_    = currency_symbol(currency_name)
        currency_min_       = currency_min(currency_name)
        currency_options    = [(currency_name, currency_symbol_, currency_min_)]


        branch_acc = BranchAccounts.objects.filter(main_account__pk=pk)
        for wallet in branch_acc:
            currency_options.append((wallet.currency, currency_symbol(wallet.currency), currency_min(wallet.currency)))
        
        context = {
            "pk"                    : pk,
            "currency_options"      : currency_options,
            "currency"              : currency_name,
            "user_currency_symbol"  : currency_symbol_,
        }
        return render(request, "wallets/currency_exchange.html", context)
    else:
        raise PermissionDenied


# def CurrencyExchangeConfirm(request, from, amount, to):
@login_required
def CurrencyExchangeConfirm(request, pk, from_, amount, to):
    if correct_user(pk):
        wallet = BranchAccounts.objects.filter(main_account__pk=pk)
        acc = account.objects.get(pk=pk)
        min_to = currency_min(to)
        min_from = currency_min(from_)
        # confirming a few things
        if min_to is None or min_from is None:
            messages.warning(request, _("You cannot exchange with the specified currencies !"))
            return redirect('accounts:home', pk=pk)
        elif from_ == to:
            messages.warning(request, _("You cannot exchange the same currencies !"))
            return redirect('accounts:home', pk=pk)
        elif wallet.filter(currency=to).exists() is False and wallet.filter(currency=from_).exists() is False or (acc.main_currency == from_ or acc.main_currency == to) is False:
            messages.warning(request, _("You do not own the specified wallets !"))
            return redirect('accounts:home', pk=pk)
        elif float(amount) < float(min_from):
            messages.warning(request, _("You have chosen a value below the minimum amount to exchange !"))
            return redirect('wallets:currency-exchange', pk=pk)
        for wallet in wallet.filter(currency=from_):
            if float(wallet.total_balance) < float(amount):
                messages.warning(request, _("You do not have enough money for this transaction !"))
                return redirect('wallets:currency-exchange', pk=pk)

        # getting the up to date rate
        url = f'https://api.exchangerate.host/convert?from={from_}&to={to}'
        response = requests.get(url) # getting a response
        data = response.json() # getting the data
        ex_rate = round(decimal.Decimal(data['result']), 4)

        if request.method == "POST":
            # updating the user's wallet
            if wallet.filter(currency=to): # sending moeny to a wallet

                # subtracting the money from the user's wallet
                wallet.filter(currency=from_).update(total_balance = F('total_balance') - float(amount))
                # or
                acc.total_balance = F('total_balance') - float(amount)
                acc.save()

                # adding the money to the user's wallet
                wallet.filter(currency=to).update(total_balance = F('total_balance') + float(amount) * float(ex_rate))
                
                # msg & redirect
                messages.success(request, _("You have successfuly exchanged your desired currencies !"))
                return redirect("accounts:home", pk=pk)
            elif acc.main_currency == to: # sending to an account
                # subtracting the money from the user's wallet
                wallet.filter(currency=from_).update(total_balance = F('total_balance') - float(amount))

                # adding the money to the user's account
                acc.total_balance = F('total_balance') + float(amount) * float(ex_rate)
                acc.save()

                # msg & redirect
                messages.success(request, _("You have successfuly exchanged your desired currencies !"))
                return redirect("accounts:home", pk=pk)
            else:
                messages.warning(request, _("You do not have a wallet with the specified currency !"))
                return redirect("wallets:wallet-search", pk=pk)

        context = {
            "from"          : from_,
            "from_symbol"   : currency_symbol(from_),
            "to"            : to,
            "to_symbol"     : currency_symbol(to),
            "amount"        : amount,
            "ex_rate"       : ex_rate,
        }
        return render(request, "wallets/currency_exchange_confirm.html", context)
    else:
        raise PermissionDenied
