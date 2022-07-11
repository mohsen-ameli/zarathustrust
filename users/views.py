import phonenumbers
import pycountry
import json

from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework import status

from accounts.models import Account
from accounts.functions import currency_min, get_currency_symbol
from .models import CustomUser, Code
from .forms import RegisterForm
from .functions import *
from .utils import phone_msg_verify
from .serializers import *


def loadConfig():
    with open('/etc/config.json') as config_file:
        return json.load(config_file)


@api_view(['POST'])
def logoutView(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
    except:
        pass
    return Response("Successful Logout")


@api_view(['POST'])
# Personal Register
def signUp(request):
    form = RegisterForm(request.data)
    
    country = request.data['country']
    ext = request.data['ext']
    username = request.data['username']
    email = request.data['email']
    password1 = request.data['password1']
    password2 = request.data['password2']

    try:
        phone_num = int(request.data['phone_number'])
    except ValueError:
        form.add_error('phone_number', 'Please enter a correct phone number')

    if CustomUser.objects.filter(email=email).exists():
        form.add_error('email', 'A user with that email address already exists!')

    phone_number = ""

    if request.user.is_anonymous == True:
        # phone number checking
        try:
            phone_number = phonenumbers.is_valid_number(phonenumbers.parse(f'+{ext}{phone_num}'))
        except Exception as e:
            form.add_error('phone_number', e)
        if phone_number is False:
            form.add_error('phone_number', 'Please enter a correct phone number')
        

        # saving the user
        if form.is_valid():
            user = {
                'username'      : username,
                'email'         : email,
                'ext'           : ext,
                'phone_number'  : phone_num,
                'country'       : country,
                'password1'     : password1,
                'password2'     : password2,
                'iban'          : None,
            }
            request.session['user'] = user

            Code.objects.create(user=user['username'])
            code_obj = Code.objects.get(user=user['username'])
            ver_code = {
                'email_verify_code' : code_obj.email_verify_code,
                'phone_verify_code' : code_obj.phone_verify_code,
                'iban_verify_code'  : code_obj.iban_verify_code,
            }
            request.session['ver_code'] = ver_code
            code_obj.delete()
    
    return Response(form.errors.as_json())


@api_view(['GET'])
# Email Verify 
def verifyEmail(request):
    config = loadConfig()
    user = request.session.get('user')
    email_code = request.session.get('ver_code')['email_verify_code']

    # send email
    EMAIL_ID = config.get("EMAIL_ID")
    send_mail(
        f"Hello {user['username']}",
        f"Your verification code is : {email_code}, you are very close to starting your money making process!",
        f"{EMAIL_ID}",
        [f"{user['email']}"],
    )

    return Response({"code": email_code})


@api_view(['GET'])
# Phone Verify 
def verifyPhone(request):
    user = request.session.get('user')
    phone_code = request.session.get('ver_code')['phone_verify_code']
    phone_number = "+" + str(user['ext']) + str(user['phone_number'])

    phone_msg_verify(
                verify_code=phone_code, phone_number_to=phone_number
            )

    return Response({"code": phone_code})


@api_view(['POST'])
# Phone Verify 
def verifyReferral(request):
    # the amount in which new user's bonus will get
    EXTRA_BONUS_VALUE = 200

    message = ""
    config  = loadConfig()

    # getting stuff to sign up the user
    user = request.session.get('user')
    
    # if user just happened to visit the page, simply redirect them back to the register page
    username        = user['username']
    email           = user['email']
    password        = user['password1']
    phone_number    = user['phone_number']
    country         = user['country']
    phone_ext       = user['ext']
    enterd_code     = request.data['code']

    iso2            = pycountry.countries.search_fuzzy(country)[0].alpha_2
    currency        = get_country_currency(iso2)
    language        = get_country_lang(iso2)
    friend          = CustomUser.objects.filter(referral_code=enterd_code)
    user_currency_min = currency_min(currency)

    # creating a user
    user = CustomUser.objects.create(username=username, password=make_password(password), email=email, phone_number=phone_number, country=iso2,
    phone_ext=phone_ext, currency=currency, iso2=iso2, language=language)

    if friend.exists():  # referral code exists
        # getting current user's stuff
        user_currency_symbol    = get_currency_symbol(currency) # their currency symbol
        user_extra_bonus        = user_currency_min * EXTRA_BONUS_VALUE

        # creating an account for the user
        bonus = (user_currency_min * 1000) + user_extra_bonus
        Account.objects.create(created_by=user, bonus=bonus, total_balance=currency_min(currency), currency=currency, iso2=iso2, primary=True, pk=user.pk)

        # getting some info from the user whose referral code was used
        refUser_pk                = friend.values("pk")[0]["pk"] # their name
        refUser_account           = Account.objects.filter(created_by__pk=refUser_pk).filter(primary=True)
        refUser_balance           = refUser_account.values('total_balance')[0]['total_balance']
        refUser_bonus             = refUser_account.values('bonus')[0]['bonus']
        refUser_currency          = refUser_account.values('currency')[0]['currency']
        refUser_email             = friend.values('email')[0]['email']
        refUser_username          = friend.values('username')[0]['username']
        refUser_currency_min      = currency_min(refUser_currency) # $1 in their currency
        refUser_extra_bonus       = refUser_currency_min * EXTRA_BONUS_VALUE
        refUser_currency_symbol   = get_currency_symbol(refUser_currency) # their currency symbol

        # updating the giver user's bonus
        refUser_account.update(
            bonus = refUser_bonus + refUser_extra_bonus,
            total_balance = refUser_balance + refUser_currency_min
        )

        # send email to the person whose referral code was just used
        EMAIL_ID = config.get("EMAIL_ID")
        send_mail(
            f"Dear {refUser_username}!",
            f"{username} just used your referral code! You recieved {refUser_currency_symbol}{refUser_currency_min} on your balance, and {refUser_currency_symbol}{refUser_extra_bonus} added to your bonus!",
            f"{EMAIL_ID}",
            [f"{refUser_email}"],
        )

        # success message
        message = f"success_register_right_referral"
        
        return Response({"msg": message, "user": username, "currency": user_currency_symbol, "extraBonus": user_extra_bonus})
    else:  # referral code not entered
        bonus = user_currency_min * 1000
        try:
            Account.objects.create(created_by=user, bonus=bonus, currency=currency, total_balance=currency_min(currency), iso2=iso2, primary=True, pk=user.pk)
        except Exception as e:
            pass

        if enterd_code == "":  # referral code not submitted
            message = f"success_register"
        else: # referral code was wrong
            message = f"success_register_wrong_referral"

        return Response({"msg": message, "user": username})


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainSerializer


class RequestPasswordResetEmail(generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ResetPasswordEmailRequestSerializer
    
    def post(self, request):
        # serializer = self.serializer_class(data=request.data)
        email = request.data['email']

        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id) )
            token = PasswordResetTokenGenerator().make_token(user)

            if settings.DEBUG:
                current_site = "localhost:3000"
            else:
                current_site = get_current_site(request=request).domain
                
            absurl = f"http://{current_site}/password-reset-confirm/{uidb64}/{token}"

            # send email
            config  = loadConfig()
            EMAIL_ID = config.get("EMAIL_ID")
            send_mail(
                f"Password reset on {current_site}",
                f"You're receiving this email because you requested a password reset for your user account at {current_site}. \n\n Please go to the following page and choose a new password: \n\n {absurl} \n\n Your username, in case you've forgotten: {user.username} \n\n Thanks for using our site! \n The {current_site} team",
                f"{EMAIL_ID}",
                [f"{user.email}"],
            )
            return Response({'msg': 'check your email to reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'No user with the specified email exists.'}, status=status.HTTP_404_NOT_FOUND)


class PasswordTokenCheck(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"error": "Token is not valid anymore. Please create a new one."}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({"success": True, "msg": "Valid Credentials.", "uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as e:
            return Response({"error": "Token is not valid anymore. Please create a new one."}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetAPIView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        return Response({"success": True, "msg": "Passowrd has been reset succefully!"}, status=status.HTTP_200_OK)
