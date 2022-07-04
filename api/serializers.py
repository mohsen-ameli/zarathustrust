from rest_framework import serializers
from accounts.models import Account, AccountInterest
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed


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


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=5)

    class Meta:
        fields = ['email']


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            uidb64 = attrs.get('uidb64')
            token = attrs.get('token')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid.", 401)

            user.set_password(password)
            user.save()

            return (user)
            
        except Exception as e:
            raise AuthenticationFailed("The reset link is invalid.", 401)
        return super().validate(attrs)
