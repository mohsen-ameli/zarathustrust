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
    path('api/currUser', views.current_user, name='currUser')
]