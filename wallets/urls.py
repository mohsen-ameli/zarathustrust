from django.urls import path
from . import views as wallet_views

app_name = "wallets"
urlpatterns = [
    path("<int:pk>/new_wallet/", wallet_views.NewWallet, name="new-wallet"),
    path("<int:pk>/currency_exchange/", wallet_views.CurrencyExchange, name="currency-exchange"),
]