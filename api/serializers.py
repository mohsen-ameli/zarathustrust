from rest_framework import serializers
from accounts.models import account, account_interest
from users.models import CustomUser

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = account
        fields = "__all__"


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = account_interest
        fields = "__all__"

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'iso2', 'currency', 'language', 'is_business')