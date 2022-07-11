from django.urls import path
from .views import *

urlpatterns = [
    path('currUser/', currentUser, name='currUser'),
    path('invite-friend/', inviteFriend, name='invite-friend'),
    path('cash-out/', cashOut, name='cash-out'),

    path('account/', accounts, name='account'),
    path('account-interest/', accountInterest, name='account-interest'),

    path('json/<str:file>/', jsonSearch, name='json-search'),

    path('transferSearch/', transferSearch, name='transfer-search'),
    path('transferConfirm/', transferConfirm, name='transfer-confirm'),

    path('deposit/', deposit, name='deposit'),
    path('withdraw/', withdraw, name='withdraw'),
    path('money-form/', moneyForm, name='money-form'),
    path('get-banking-info/', getBankingInfo, name='get-banking-info'),
    
    path('wallets/', wallets, name='wallets'),
    path('wallets-confirm/', walletsConfirm, name='wallets-confirm'),

    path('getCurrencySymbol/<str:country>/', getCurrencySymbol, name='get-currency-symbol'),
    path('currency-exchange/<str:fromCurr>/<str:fromIso>/<str:amount>/<str:toCurr>/<str:toIso>/', currencyEx, name='currency-exchange'),

    path('transactions/<str:walletIso>/<str:walletName>/<int:pageNum>/<int:numItems>/', transactions, name="transactions"),
    path('transactions/<int:tId>/', transactionDetail, name='transaction-detail'),
]
