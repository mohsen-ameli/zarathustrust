import json
import os
import phonenumbers
import pycountry

from django.core.mail import send_mail, EmailMessage
from django.db.models import Q, F
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework import status

from accounts.functions import *
from accounts.models import *
from users.models import CustomUser, code
from users.forms import RegisterForm
from users.functions import *
from users.utils import phone_msg_verify
from .serializers import *


def loadConfig():
    with open('/etc/config.json') as config_file:
        return json.load(config_file)


def loadJson(filename):
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/{filename}.json'

    with open(file, 'r') as json_currency:
        return json.load(json_currency)


@api_view(['POST'])
def logoutView(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
    except:
        pass
    return Response("Successful Logout")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accounts(request):
    try:
        user = Account.objects.get(pk=request.user.pk)
    except:
        user = None
    serializer = AccountSerializer(instance=user, many=False)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accountInterest(request):
    try:
        user = AccountInterest.objects.get(pk=request.user.pk)
    except:
        user = None
    serializer = InterestSerializer(instance=user, many=False)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def currentUser(request):
    try:
        user = CustomUser.objects.get(pk=request.user.pk)
    except:
        user = None
    serializer = CustomUserSerializer(instance=user, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def jsonSearch(request, file):
    return Response(loadJson(file))


@api_view(['GET'])
def getCurrencySymbol(request, country):
    try:
        data = loadJson("currencies_symbols")

        return Response(data[country.upper()])
    except Exception:
        return Response({})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cashOut(request):
    # settings variables
    pk                = request.user.pk
    account           = Account.objects.filter(created_by__pk=pk).get(primary=True)
    accInterest       = AccountInterest.objects.get(pk=pk)
    interest_rate     = accInterest.interest_rate
    bonus             = account.bonus
    total_balance     = account.total_balance

    # checking insufficient interest amount
    if interest_rate < 0.1:
        return Response({"failed": "You need at least $0.1 to be able to cash out!"})

    # checking bonus if it's more than interest rate or not
    if interest_rate <= bonus:
        extra = (round(interest_rate, 1) * 2)
        account.bonus = F('bonus') - interest_rate
    else:
        extra = bonus + interest_rate
        account.bonus = 0

    total_balance = total_balance + extra

    # updaing everyting
    account.total_balance = total_balance
    accInterest.interest = total_balance
    accInterest.interest_rate = 0

    transaction = TransactionHistory(person=account, price=round(extra, 1), method="Cash Out")

    transaction.save()
    account.saveView()
    accInterest.save()
    account.refresh_from_db()
    accInterest.refresh_from_db()

    return Response({"success": True, "balance": total_balance, "amount": round(extra, 1)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit(request):
    pk              = request.user.pk
    config          = loadConfig()
    user            = CustomUser.objects.get(pk=pk)

    body = json.loads(request.body)
    symbol          = body['symbol']
    amount          = body['amount']
    EMAIL_ID        = config.get('EMAIL_ID')
    EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')

    send_mail(f'DEPOSIT FOR {user.username}', 
            f'{user.username} with account number : {pk} has requested to deposit {symbol}{amount}',
            f'{EMAIL_ID}',
            [f'{EMAIL_ID_MAIN}']
    )

    return Response({"success": True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    success             = False
    config              = loadConfig()
    pk                  = request.user.pk

    body                = json.loads(request.body)
    moneyToWithdraw     = float(body['money'])
    currency            = body['currency']

    user                = CustomUser.objects.get(pk=pk)
    account             = Account.objects.filter(created_by=user).get(currency=currency)
    balance             = account.total_balance

    userCurrencySymbol  = get_currency_symbol(currency)
    minMoney            = float(currency_min(currency))

    if moneyToWithdraw >= minMoney and moneyToWithdraw <= balance:
        # sending email to admin and user
        EMAIL_ID        = config.get('EMAIL_ID')
        EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')
        MOE_EMAIL       = config.get('MOE_EMAIL')
        send_mail(f'WITHDRAW FOR {user.username}', 
                f'{user.username} with account number {pk} has requested to withdraw {userCurrencySymbol}{moneyToWithdraw}',
                f'{EMAIL_ID}',
                [f'{EMAIL_ID_MAIN}'],)

        account.take_money = round(decimal.Decimal(moneyToWithdraw), 2)
        account.saveView()

        # success
        success = True
        
    return Response({"userCurrencySymbol" : userCurrencySymbol, "minCurrency": minMoney, "success": success})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def moneyForm(request):
    pk                  = request.user.pk
    accounts            = Account.objects.filter(created_by__pk=pk)

    # currencies that will be showed as options
    currencyOptions     = []

    for account in accounts:
        currencyOptions.append((account.iso2, account.currency, get_currency_symbol(account.currency), currency_min(account.currency)))
    
    return Response({'currencyOptions': currencyOptions})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallets(request):
    return Response(getWallets(request.user.pk))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def walletsConfirm(request):
    MAX_NUMBER_WALLETS = 10
    pk       = request.user.pk
    body     = json.loads(request.body)
    currency = body['currency']
    iso2     = body['iso2']

    main_account = Account.objects.filter(created_by__pk=pk)

    if not main_account.__len__() <= MAX_NUMBER_WALLETS:
        return Response({"success": False, "msg": "too_many_wallets"})

    if not main_account.filter(iso2=iso2).exists():
        Account.objects.create(created_by=main_account.get(primary=True).created_by, currency=currency, iso2=iso2, primary=False)
        return Response({"success": True, "msg": "new_wallet_success"})
    else:
        return Response({"success": False, "msg": "wallet_error"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transferSearch(request):
    body = json.loads(request.body)
    typed = body['person']
    
    query = CustomUser.objects.all().filter(
                Q(email__iexact=typed) | Q(phone_number__iexact=typed) | Q(username__iexact=typed)
            )
    if len(query) > 0 and len(typed) > 2:
        res = None
        data = []
        for obj in query:
            item = {
                'pk' : obj.pk,
                'username' : obj.username,
            }
            data.append(item)
        res = data
    else:
        res = None
        
    return Response(json.dumps(res))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transferConfirm(request):
    config                   = loadConfig()
    pk                       = request.user.pk
    success                  = False
    message                  = ""

    # form vars
    body                     = json.loads(request.body)
    reciever_name            = body['reciever_name']
    purpose                  = body['purpose']
    money                    = float(body['moneyToSend'])
    currency                 = body['currency']

    # user's stuff
    currencyName             = currency.upper()
    userCurrencySymbol       = get_currency_symbol(currencyName)
    minCurrency              = currency_min(currencyName)

    giver_user               = CustomUser.objects.get(pk=pk)
    reciever_user            = CustomUser.objects.get(username=reciever_name)

    # Logic starts
    try:
        # getting giver/reciever stuff
        giver                    = Account.objects.filter(created_by__pk=pk).get(currency=currency)
        reciever                 = Account.objects.filter(created_by__username=reciever_name)
        if not reciever.filter(currency=currency).exists():
            reciever = Account.objects.create(created_by=reciever_user, currency=currency, iso2=iso3_to_iso2(currency), primary=False)
        else:
            reciever = reciever.get(currency=currency)

        giver_balance            = giver.total_balance

        # if user has entered the bare minimum, and if has enough money
        if money >= minCurrency and money <= giver_balance:    
            # updating the reciever
            reciever.add_money = decimal.Decimal(money)
            reciever.saveView()

            # updating the giver
            giver.take_money = decimal.Decimal(money)
            giver.saveView()

            # recording the transaction
            TransactionHistory.objects.create(person=giver, second_person=reciever, price=money, purpose_of_use=purpose, method="Transfer")

            # success message
            message = f"{userCurrencySymbol}{money} has been transfered to {reciever_name}"
            success = True

            # emailing the reciever
            reciever_email = reciever_user.email
            giver_username = giver_user.username
            giver_email    = giver_user.email
            EMAIL_ID       = config.get('EMAIL_ID')

            if purpose is not None:
                body = f"Dear {reciever_name}, <br> {giver_username} just transfered {userCurrencySymbol}{round(money, 1)} to your account! <br> Message: {purpose}"
            else:
                body = f"Dear {reciever_name}, <br> {giver_username} just transfered {userCurrencySymbol}{round(money, 1)} to your account!"
            msg = EmailMessage(("ZARATHUSTRUST MONEY TRANSFER"),
                    body,
                    f"{EMAIL_ID}",
                    [f"{reciever_email}"]
            )
            msg.content_subtype = "html"
            msg.send()

            # emailing the giver
            if purpose is not None:
                body = f"Dear {giver_username}, <br> {userCurrencySymbol}{round(money, 1)} has been transfered to {reciever_name} successfully! <br> Message: {purpose}"
            else:
                body = f"Dear {giver_username}, <br> {userCurrencySymbol}{round(money, 1)} has been transfered to {reciever_name} successfully!"
            msg1 = EmailMessage(("ZARATHUSTRUST MONEY TRANSFER"),
                    body,
                    f"{EMAIL_ID}",
                    [f"{giver_email}"]
            )
            msg1.content_subtype = "html"
            msg1.send()

        elif money < minCurrency:
            message = f"Please consider that the minimum amount to send is {userCurrencySymbol}{minCurrency}!"
        elif money > giver_balance:
            message = "more_than_ballance"
    except ObjectDoesNotExist:
        message = "hasnt_finished_signup"

    return Response({"message" : message, "success": success})


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def currencyEx(request, fromCurr, fromIso, amount, toCurr, toIso):
    pk       = request.user.pk
    message  = ""
    success  = True
    toCurr   = toCurr.upper()
    fromCurr = fromCurr.upper()

    account  = Account.objects.filter(created_by__pk=pk)

    minTo    = currency_min(toCurr)
    minFrom  = currency_min(fromCurr)

    #-------------------------------- CHECKS ------------------------------#
    if minTo is None or minFrom is None: # the currency doesnt exist
        message = "exchange_specified_error"
        return Response({"message": message, "success": False})
    elif fromCurr == toCurr: # exchanging the same currencies
        message = "exchange_same_error"
        return Response({"message": message, "success": False})
    elif not account.filter(currency=toCurr, iso2=toIso).exists() and account.currency != toCurr:
        message = "exchange_not_have_error"
        return Response({"message": message, "success": False})
    elif not account.filter(currency=fromCurr, iso2=fromIso).exists() and account.currency != fromCurr:
        message = "exchange_not_have_error"
        return Response({"message": message, "success": False})
    
    to_account = account.get(currency=toCurr, iso2=toIso)
    from_account = account.get(currency=fromCurr, iso2=fromIso)

    total_balance = from_account.total_balance

    if float(total_balance) < float(amount): # if user has enough money
        message = "not_enough_money"
        return Response({"message": message, "success": False})
    #-------------------------------- CHECKS ------------------------------#

    #-------------------------------- LOGIC ------------------------------#
    # getting the up to date rate
    url = f'https://api.exchangerate.host/convert?from={fromCurr}&to={toCurr}'
    response = requests.get(url)
    data = response.json()
    ex_rate = round(decimal.Decimal(data['result']), 4)

    if request.method == "POST": # doing the transaction
        from_account.take_money = decimal.Decimal(amount)
        from_account.saveView()

        # adding the money toCurr the user's account
        to_account.add_money = decimal.Decimal(amount) * decimal.Decimal(ex_rate)
        to_account.saveView()

        # saving this transaction
        transaction = TransactionHistory(
            person=from_account,
            second_person=to_account, 
            price=float(amount), 
            ex_rate=ex_rate, 
            exchanged_price=float(amount) * float(ex_rate), 
            method="Exchange"
        )
        transaction.save()

        # msg & redirect
        message = "success_ex"
        success = True

    return Response({"message": message, "success": success, "ex_rate": ex_rate})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactions(request, walletIso, walletName, pageNum, numItems):
    pk             = request.user.pk

    account        = Account.objects.get(created_by__pk=pk, currency=walletName, iso2=walletIso)
    transactions   = TransactionHistory.objects.none()

    # wallet's currency symbol
    currency_symbol = get_currency_symbol(walletName)

    # getting account's transactions
    person_history         = TransactionHistory.objects.filter(person=account).order_by('date').reverse()
    seconed_person_history = TransactionHistory.objects.filter(second_person=account).order_by('date').reverse()
    transactions = person_history | seconed_person_history
    
    # total number of transactions
    counter = transactions.count()

    # user wants to see all of their transactions
    if numItems == 0:
        numItems = counter
    if counter == 0:
      numItems = 1  

    paginator   = Paginator(transactions, numItems)
    page_obj    = paginator.get_page(pageNum)

    transactions = []

    for item in page_obj:
        id      = item.id
        person  = [item.person.created_by.username, item.person.currency] if item.person else "Anonymous"
        person2 = item.second_person.created_by.username if item.second_person else "Anonymous"

        newItem = {
            "id"        : id,
            "type"      : item.method,
            "price"     : item.price,
            "exPrice"   : item.exchanged_price,
            "date"      : [item.date.year, item.date.month, item.date.day, item.date.hour, item.date.minute, item.date.second],
            "person"    : person,
            "person2"   : person2,
        }

        transactions.append(newItem)

    context = {
        "transactions"         : transactions, 
        "counter"              : counter,
        "currencySymbol"       : currency_symbol,
    }

    return Response(context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactionDetail(request, tId):
    incoming = 0
    transactor = None
    incom = False
    giver_symbol = None
    reciever_symbol = None
    transaction = TransactionHistory.objects.get(pk=tId)

    currency = transaction.person.currency or transaction.second_person.currency
    currency_symbol   = get_currency_symbol(currency)
    
    if transaction.method == "Transfer":
        # if user is sending money
        if transaction.person.created_by == request.user:
            incoming = 0
            try:
                transactor = transaction.second_person.created_by.username
            except AttributeError:
                transactor = "Anonymous"
        else:
            incom = True
        # user is recieving moeny
        if incom == True:
            incoming = 1
            try:
                transactor  = transaction.person.created_by.username
            except AttributeError:
                transactor = "Anonymous"
    elif transaction.method == "Exchange":
        giver_symbol = get_currency_symbol(transaction.person.currency)
        reciever_symbol = get_currency_symbol(transaction.second_person.currency)


    person  = [transaction.person.created_by.username, transaction.person.currency] if transaction.person else "Anonymous"
    person2 = transaction.second_person.created_by.username if transaction.second_person else "Anonymous"

    data = [{
        "type"          : transaction.method,
        "price"         : transaction.price,
        "exPrice"       : transaction.exchanged_price,
        "date"          : json.dumps(transaction.date.strftime('%Y-%m-%d %H:%M:%S %Z')),
        "message"       : transaction.purpose_of_use,
        "person"        : person,
        "person2"       : person2,
    }]

    context = {
        "transaction"       : data,
        "currency_symbol"   : currency_symbol,
        "incoming"          : incoming,
        "transactor"        : transactor,
        "giverSymbol"      : giver_symbol,
        "recieverSymbol"   : reciever_symbol,
    }

    return Response(context)


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

            code.objects.create(user=user['username'])
            code_obj = code.objects.get(user=user['username'])
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


# Referral Code
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inviteFriend(request):
    code = CustomUser.objects.get(pk=request.user.pk).referral_code
    return Response({"code" : code})