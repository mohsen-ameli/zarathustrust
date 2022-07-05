from unicodedata import name
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('token/', views.EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logoutView, name='logout'),
    path('signup/', views.signUp, name='sign-up'),
    path('verify-email/', views.verifyEmail, name='verify-email'),
    path('verify-phone/', views.verifyPhone, name='verify-phone'),
    path('verify-referral/', views.verifyReferral, name='verify-referral'),
    path('password-reset/', views.RequestPasswordResetEmail.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', views.PasswordTokenCheck.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', views.PasswordResetAPIView.as_view(), name='password-complete'),

    path('currUser/', views.currentUser, name='currUser'),
    path('account/', views.accounts, name='account'),
    path('account-interest/', views.accountInterest, name='account-interest'),
    path('json/<str:file>/', views.jsonSearch, name='json-search'),
    path('getCurrencySymbol/<str:country>/', views.getCurrencySymbol, name='get-currency-symbol'),
    path('cash-out/', views.cashOut, name='cash-out'),
    path('transferSearch/', views.transferSearch, name='transfer-search'),
    path('transferConfirm/', views.transferConfirm, name='transfer-confirm'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('money-form/', views.moneyForm, name='money-form'),
    path('wallets/', views.wallets, name='wallets'),
    path('wallets-confirm/', views.walletsConfirm, name='wallets-confirm'),
    path('transactions/<str:walletIso>/<str:walletName>/<int:pageNum>/<int:numItems>/', views.transactions, name="transactions"),
    path('transactions/<int:tId>/', views.transactionDetail, name='transaction-detail'),
    path('currency-exchange/<str:fromCurr>/<str:fromIso>/<str:amount>/<str:toCurr>/<str:toIso>/', views.currencyEx, name='currency-exchange'),
]
