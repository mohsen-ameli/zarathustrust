from rest_framework import serializers
from accounts.models import Account, AccountInterest
from users.models import CustomUser

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountInterest
        fields = "__all__"

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'iso2', 'currency', 'language', 'is_business')