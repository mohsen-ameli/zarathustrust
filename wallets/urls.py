from os import name
from django.urls import path
from . import views as wallet_views

app_name = "wallets"
urlpatterns = [
    path("<int:pk>/new_wallet/", wallet_views.WalletSearch, name="wallet-search"),
    path("<int:pk>/new_wallet/<str:currency>/", wallet_views.NewWallet, name="new-wallet"),
    path("<int:pk>/currency_exchange/", wallet_views.CurrencyExchange, name="currency-exchange"),
    path("<int:pk>/currency_exchange/<str:from_>/<str:amount>/<str:to>", wallet_views.CurrencyExchangeConfirm, name="currency-exchange-confirm"),
    
    path("<int:pk>/card_or_bank", wallet_views.Card_or_Bank, name="card_or_bank"),
    path("<int:pk>/new_card", wallet_views.Card, name="new-card"),
    path("<int:pk>/new_bank", wallet_views.Bank, name="new-bank")
]