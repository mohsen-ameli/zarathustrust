from unicodedata import name
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('accounts', views.AccountsApi, 'accounts')
router.register('users', views.UsersApi, 'users')
router.register('interest', views.InterestApi, 'interest')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/currUser/', views.current_user, name='currUser'),
    path('api/countryCurrencies/', views.countryCurrencies, name='country-currencies'),
    path('api/countries/', views.countries, name='countries'),
    path('api/transferSearch', views.transferSearch, name='transfer-search'),
    path('api/transferConfirm', views.transferConfirm, name='transfer-confirm'),
    path('api/<int:pk>/deposit', views.deposit, name='deposit'),
    path('api/<int:pk>/withdraw', views.withdraw, name='withdraw'),
    path('api/<int:pk>/money-form', views.moneyForm, name='money-form'),
    path('api/<int:pk>/', views.wallets, name='wallets'),
    path('api/<int:pk>/<str:currency>/', views.walletsConfirm, name='new-wallet'),
]
