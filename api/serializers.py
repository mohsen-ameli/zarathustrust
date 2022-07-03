from rest_framework import serializers, exceptions
from accounts.models import Account, AccountInterest
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainSerializer, api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q


class EmailTokenObtainSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)
        
    def validate(self, attrs):
        # searching for the username based on the input
        user = CustomUser.objects.all().filter(
            Q(email__iexact=attrs[self.username_field]) | Q(username__iexact=attrs[self.username_field])
        )

        # getting the username of the user
        for obj in user:
            username = obj.username

        # doing everything else from the original parent class
        data = super().validate({self.username_field:username, "password":attrs['password']})

        # getting out two tokens
        refresh = self.get_token(self.user)

        # setting those two tokens
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        # returning them tokens
        return data


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