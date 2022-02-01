from django.shortcuts import render


def NewWallet(request, pk):
    context = {
        "pk" : pk,
    }
    return render(request, "wallets/new_wallet.html", context)


def CurrencyExchange(request, pk):
    context = {
        "pk" : pk,
    }
    return render(request, "wallets/currency_exchange.html", context)