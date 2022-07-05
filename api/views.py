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
from users.models import CustomUser, code, ReferralCode
from users.forms import RegisterForm
from users.functions import *
from users.utils import phone_msg_verify
from wallets.models import BranchAccounts
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
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/{file}.json' # getting the file containing all country codes

    with open(file, 'r') as json_currency: # opening and reading the json file
        data = json.load(json_currency)

    return Response(data)

@api_view(['GET'])
def getCurrencySymbol(request, country):
    try:
        country_code = country.upper()
        project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file = f'{project}/json/currencies_symbols.json' # getting the file containing all country codes
        with open(file, 'r') as config_file: # opening and reading the json file
            data = json.load(config_file)

        return Response(data[country_code])
    except:
        return Response({})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cashOut(request):
    # settings variables
    pk                = request.user.pk
    acc               = Account.objects.get(pk=pk)
    accInterest       = AccountInterest.objects.get(pk=pk)
    interest_rate     = accInterest.interest_rate
    bonus             = acc.bonus
    total_balance     = acc.total_balance

    # checking insufficient interest amount
    if interest_rate < 0.1:
        return Response({"failed": "You need at least $0.1 to be able to cash out!"})

    # checking bonus if it's more than interest rate or not
    if interest_rate <= bonus:
        extra = (round(interest_rate, 1) * 2)
        acc.bonus = F('bonus') - interest_rate
    else:
        extra = bonus + interest_rate
        acc.bonus = 0

    total_balance = total_balance + extra

    # updaing everyting
    acc.total_balance = total_balance
    accInterest.interest = total_balance
    accInterest.interest_rate = 0

    r = TransactionHistory(person=acc, price=round(extra, 1), method="Cash Out")

    r.save()
    acc.save()
    accInterest.save()
    acc.refresh_from_db()
    accInterest.refresh_from_db()

    return Response({"success": True, "balance": total_balance, "amount": round(extra, 1)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit(request):
    pk              = request.user.pk
    config          = loadConfig()
    user            = CustomUser.objects.get(pk=pk)

    body = json.loads(request.body)
    print("request : ", json.loads(request.body))
    symbol          = body['symbol']
    amount          = body['amount']
    EMAIL_ID        = config.get('EMAIL_ID')
    EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')

    send_mail(f'DEPOSIT FOR {user.username}', 
            f'{user.username} with account number : {pk} has requested to deposit {symbol}{amount}',
            f'{EMAIL_ID}',
            [f'{EMAIL_ID_MAIN}'],)

    Account.objects.filter(pk=pk).update(add_money=0)
    
    return Response({"message": "success", "success": True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    pk                  = request.user.pk
    body                = json.loads(request.body)
    config              = loadConfig()
    success             = False
    user                = CustomUser.objects.get(pk=pk)
    acc                 = Account.objects.get(pk=pk)
    allBranchAcc        = BranchAccounts.objects.filter(main_account__pk=pk)

    moneyToWithdraw     = float(body['money'])
    currency            = body['currency']

    userCurrencySymbol  = get_currency_symbol(currency)
    minCurrency         = float(currency_min(currency))

    branchAcc           = allBranchAcc.filter(currency=currency)
    if branchAcc.exists(): # working with wallet
        balance = branchAcc.values("total_balance")[0]['total_balance']
    else: # working with account
        balance = acc.total_balance


    if moneyToWithdraw >= minCurrency and moneyToWithdraw <= balance:
        # sending email to admin and user
        EMAIL_ID        = config.get('EMAIL_ID')
        EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')
        MOE_EMAIL       = config.get('MOE_EMAIL')
        send_mail(f'WITHDRAW FOR {user.username}', 
                f'{user.username} with account number {pk} has requested to withdraw {userCurrencySymbol}{moneyToWithdraw}',
                f'{EMAIL_ID}',
                [f'{EMAIL_ID_MAIN}'],)


        if branchAcc.exists(): # withdrawing from wallet
            branchAcc.update(total_balance=F('total_balance') - moneyToWithdraw)
            branchAcc.update(take_money=0)
        else: # withdrawing from account
            acc.take_money = 0
            acc.total_balance = F('total_balance') - moneyToWithdraw
            acc.save()

        # success message
        success = True
        
    return Response({"userCurrencySymbol" : userCurrencySymbol, "minCurrency": minCurrency, "success": success})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def moneyForm(request):
    pk                  = request.user.pk
    acc                 = Account.objects.get(pk=pk)
    branchAcc           = BranchAccounts.objects.filter(main_account__pk=pk)

    currency            = acc.main_currency
    iso2                = acc.iso2

    userCurrencySymbol  = get_currency_symbol(currency)
    minCurrency         = currency_min(currency)

    currencyOptions     = [(iso2, currency, userCurrencySymbol, minCurrency)] # currencies that will be showed as options

    for wallet in branchAcc:
        currencyOptions.append((wallet.iso2, wallet.currency, get_currency_symbol(wallet.currency), currency_min(wallet.currency)))
    
    return Response({'currencyOptions': currencyOptions})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallets(request):
    pk              = request.user.pk
    acc             = Account.objects.get(pk=pk)
    branchAccount   = BranchAccounts.objects.filter(main_account__pk=pk)

    wallets = user_wallets(branchAccount, acc)

    return Response(wallets)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def walletsConfirm(request):
    pk       = request.user.pk
    body     = json.loads(request.body)
    currency = body['currency']
    iso2     = body['iso2']
    success  = False

    main_account = Account.objects.get(pk=pk)

    if (iso2 != main_account.iso2):
        branch = BranchAccounts.objects.get_or_create(main_account=main_account, currency=currency, iso2=iso2)
        success = branch[1]

    return Response({"success": success})



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
    # react variables
    config                   = loadConfig()
    pk                       = request.user.pk
    body                     = json.loads(request.body)
    reciever_name            = body['reciever_name']
    purpose                  = body['purpose']
    moneyToSend              = float(body['moneyToSend'])
    currency                 = body['currency']
    success                  = False

    # getting user's currency stuff
    currencyName             = currency.upper()
    userCurrencySymbol       = get_currency_symbol(currency.upper())
    minCurrency              = currency_min(currencyName)

    
    # Logic starts
    try:
        # getting giver/reciever stuff
        giver                    = Account.objects.get(pk=pk)
        reciever                 = Account.objects.get(created_by__username=reciever_name)
        giver_wallet             = BranchAccounts.objects.filter(main_account=giver)

        # testing to see if we are withdrawing to a wallet
        test = BranchAccounts.objects.filter(main_account__pk=pk).filter(currency=currency).exists()
        if test:
            balance              = BranchAccounts.objects.filter(main_account=giver).get(currency=currency.upper()).total_balance
        else: # sending to account, therefore using account balance
            balance              = giver.total_balance
        
        giver_currency           = giver.main_currency
        reciever_currency        = reciever.main_currency

        if giver != reciever: # making sure the user isn't sending money to themselves
            giver_interest      = AccountInterest.objects.get(pk=pk)
            reciever_interest   = AccountInterest.objects.get(pk=reciever.pk)

            # if user has entered the bare minimum, and if has enough money
            if moneyToSend >= minCurrency and moneyToSend <= balance:

                ######## SETTING VARIABLES FOR THE UPDATE ########
                reciever_wallet     = BranchAccounts.objects.filter(main_account=reciever)
                reciever_specific   = reciever_wallet.filter(currency=currencyName)
                # reciever and giver's accounts do not have the same currency
                if giver_currency == currencyName: # account-to-somthing
                    giver_total_balance = balance
                    giver_update = Account.objects.filter(pk=pk)
                    if reciever_specific.exists():
                        # account-to-wallet
                        print("account-to-wallet")

                        reciever_total_balance = reciever_specific.values("total_balance")[0]['total_balance']
                        reciever_update = reciever_specific
                        update_interest_rate = False

                        # recording the transaction
                        r = TransactionHistory(person=giver, second_wallet=reciever_specific.get(main_account=reciever),
                        price=moneyToSend, purpose_of_use=purpose, method="Transfer")
                    elif giver_currency == reciever_currency and currencyName:
                        # account-to-account
                        print("account-to-account")

                        reciever_total_balance = reciever.total_balance
                        reciever_update = Account.objects.filter(created_by__username=reciever_name)
                        update_interest_rate = True

                        # recording the transaction
                        r = TransactionHistory(person=giver, second_person=reciever,
                        price=moneyToSend, purpose_of_use=purpose, method="Transfer")
                    else:
                        # account-to-newWallet
                        print("account-to-newWallet")
                        # creating a new wallet for reciever
                        new = BranchAccounts(main_account=reciever, currency=giver_currency)
                        new.save()
                        reciever_total_balance = 0
                        reciever_update = BranchAccounts.objects.filter(main_account=reciever)
                        update_interest_rate = False

                        # recording the transaction
                        r = TransactionHistory(person=giver, second_wallet=new,
                        price=moneyToSend, purpose_of_use=purpose, method="Transfer")
                else: # wallet-to-something
                    giver_total_balance = giver_wallet.filter(currency=currencyName).values("total_balance")[0]['total_balance']
                    giver_update = giver_wallet.filter(currency=currencyName)
                    abc = giver_wallet.get(currency=currencyName)
                    if reciever_specific.exists():
                        # wallet-to-wallet
                        print("wallet-to-wallet")
                        reciever_total_balance = reciever_specific.values("total_balance")[0]['total_balance']
                        reciever_update = reciever_specific
                        update_interest_rate = False

                        # recording the transaction
                        r = TransactionHistory(wallet=abc, second_wallet=reciever_wallet.get(currency=currencyName),
                        price=moneyToSend, purpose_of_use=purpose, method="Transfer")
                    elif reciever.main_currency == currencyName:
                        # wallet-to-account
                        print("wallet-to-account")
                        reciever_total_balance = reciever.total_balance
                        reciever_update = Account.objects.filter(created_by__username=reciever_name)
                        update_interest_rate = True

                        # recording the transaction
                        r = TransactionHistory(wallet=abc, second_person=reciever,
                        price=moneyToSend, purpose_of_use=purpose, method="Transfer")
                    else:
                        # wallet-to-newWallet
                        print("wallet-to-newWallet")
                        # creating a new wallet for reciever
                        new = BranchAccounts(main_account=reciever, currency=currencyName)
                        new.save()
                        reciever_total_balance = 0
                        reciever_update = BranchAccounts.objects.filter(main_account=reciever)
                        update_interest_rate = False
                        
                        # recording the transaction
                        r = TransactionHistory(wallet=abc, second_wallet=new,
                        price=moneyToSend, purpose_of_use=purpose, method="Transfer")
                
                ######## UPDATING ########
                # adding money to reciever
                new_total_balance = float(reciever_total_balance) + moneyToSend
                # updating the reciever
                reciever_update.update(total_balance=new_total_balance)
                # taking money from giver
                rmv_total_balance = float(giver_total_balance) - moneyToSend
                # updating the giver
                giver_update.update(total_balance=rmv_total_balance)

                ######## UPDATE ACCOUNT INTEREST ########
                if update_interest_rate is True:
                    # updaing account interest
                    reciever_interest.interest = F('interest') + moneyToSend
                    reciever_interest.save()
                # taking money from giver
                b = float(giver_interest.interest) - moneyToSend
                # updating giver
                AccountInterest.objects.filter(pk=pk).update(interest=b)



                # success message
                message = f"{userCurrencySymbol}{moneyToSend} has been transfered to {reciever_name}"

                # emailing the reciever
                reciever_email = CustomUser.objects.get(pk=reciever.pk).email
                giver_username = CustomUser.objects.get(pk=pk).username
                giver_email = CustomUser.objects.get(pk=pk).email
                EMAIL_ID       = config.get('EMAIL_ID')

                if purpose is not None:
                    body = f"Dear {reciever_name}, <br> {giver_username} just transfered {userCurrencySymbol}{round(moneyToSend, 1)} to your account! <br> Message: {purpose}"
                else:
                    body = f"Dear {reciever_name}, <br> {giver_username} just transfered {userCurrencySymbol}{round(moneyToSend, 1)} to your account!"
                msg = EmailMessage(("ZARATHUSTRUST MONEY TRANSFER"),
                        body,
                        f"{EMAIL_ID}",
                        [f"{reciever_email}"]
                )
                msg.content_subtype = "html"
                msg.send()

                # emailing the giver
                if purpose is not None:
                    body = f"Dear {giver_username}, <br> {userCurrencySymbol}{round(moneyToSend, 1)} has been transfered to {reciever_name} successfully! <br> Message: {purpose}"
                else:
                    body = f"Dear {giver_username}, <br> {userCurrencySymbol}{round(moneyToSend, 1)} has been transfered to {reciever_name} successfully!"
                msg1 = EmailMessage(("ZARATHUSTRUST MONEY TRANSFER"),
                        body,
                        f"{EMAIL_ID}",
                        [f"{giver_email}"]
                )
                msg1.content_subtype = "html"
                msg1.send()

                # add the transaction to the user's history
                r.save()

                # success is true if successful
                success = True

            elif moneyToSend < minCurrency:
                message = f"Please consider that the minimum amount to send is {userCurrencySymbol}{minCurrency}!"
            elif moneyToSend > balance:
                message = "more_than_ballance"
        else:
            message = "cannot_send_to_self"
    except ObjectDoesNotExist:
        message = "hasnt_finished_signup"

    return Response({"message" : message, "success": success})


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def currencyEx(request, fromCurr, fromIso, amount, toCurr, toIso):
    pk                  = request.user.pk
    message             = ""
    success             = True
    notEnough           = False
    toCurr              = toCurr.upper()
    fromCurr            = fromCurr.upper()

    wallet              = BranchAccounts.objects.filter(main_account__pk=pk)
    accInterest         = AccountInterest.objects.get(pk=pk)
    acc                 = Account.objects.get(pk=pk)

    minTo               = currency_min(toCurr)
    minFrom             = currency_min(fromCurr)

    #-------------------------------- CHECKS ------------------------------#
    # confirming from and to currencies
    if minTo is None or minFrom is None: # the currency doesnt exist (JXL)
        message = "88You cannot exchange with the specified currencies!"
        return Response({"message": message, "success": False})
    elif fromCurr == toCurr: # exchanging the same currencies
        message = "You cannot exchange the same currencies!"
        return Response({"message": message, "success": False})
    elif not wallet.filter(currency=toCurr, iso2=toIso).exists() and acc.main_currency != toCurr:
        message = "You do not own the specified wallets!"
        return Response({"message": message, "success": False})
    elif not wallet.filter(currency=fromCurr, iso2=fromIso).exists() and acc.main_currency != fromCurr:
        message = "You do not own the specified wallets!"
        return Response({"message": message, "success": False})

    # if user has enough money
    if fromCurr == acc.main_currency:
        if float(acc.total_balance) < float(amount):
            notEnough = True
    else:
        for wallet in wallet.filter(currency=fromCurr, iso2=fromIso):
            if float(wallet.total_balance) < float(amount):
                notEnough = True
    if notEnough:
        message = "You do not have enough money for this transaction!"
        return Response({"message": message, "success": False})
    #-------------------------------- CHECKS ------------------------------#

    #-------------------------------- LOGIC ------------------------------#
    # getting the up to date rate
    url = f'https://api.exchangerate.host/convert?from={fromCurr}&to={toCurr}'
    response = requests.get(url) # getting a response
    data = response.json() # getting the data
    ex_rate = round(decimal.Decimal(data['result']), 4)

    if request.method == "POST": # doing the transaction
        # idk why django gives an error without this line smh
        wallet = BranchAccounts.objects.filter(main_account__pk=pk)

        # sending to a wallet
        if wallet.filter(currency=toCurr, iso2=toIso): 

            # subtracting the money from the user's wallet
            acc.total_balance = F('total_balance') - float(amount)
            acc.save()

            # adding the money to the user's wallet
            wallet.filter(currency=toCurr, iso2=toIso).update(total_balance = F('total_balance') + float(amount) * float(ex_rate))
            
            # updating user's interest_account
            accInterest.interest = F('interest') - float(amount)
            accInterest.save()

            # sending from account to wallet
            if fromCurr == CustomUser.objects.get(pk=pk).currency:
                history = TransactionHistory(
                    person=acc, 
                    second_wallet=wallet.get(currency=toCurr, iso2=toIso), 
                    price=float(amount), 
                    ex_rate=ex_rate, 
                    exchanged_price=float(amount) * float(ex_rate), 
                    method="Exchange"
                )
            # sending from another wallet to wallet
            else:
                history = TransactionHistory(
                    wallet=wallet.get(currency=fromCurr, iso2=fromIso), 
                    second_wallet=wallet.get(currency=toCurr, iso2=toIso), 
                    price=float(amount), 
                    ex_rate=ex_rate, 
                    exchanged_price=float(amount) * float(ex_rate), 
                    method="Exchange"
                )
            # saving this transaction to history
            history.save()

            # success msg & redirect
            message = "You have successfuly exchanged your desired currencies!"
            success = True
        
        # sending to an account
        elif acc.main_currency == toCurr: 
            # subtracting the money from the user's wallet
            wallet.filter(currency=fromCurr, iso2=fromIso).update(total_balance = F('total_balance') - float(amount))

            # adding the money toCurr the user's account
            acc.total_balance = F('total_balance') + float(amount) * float(ex_rate)
            acc.save()

            # updating user's interest_account
            accInterest.interest = F('interest') + float(amount) * float(ex_rate)
            accInterest.save()

            # saving this transaction to history
            history = TransactionHistory(
                wallet=wallet.get(currency=fromCurr, iso2=fromIso), 
                second_person=acc, 
                price=float(amount), 
                ex_rate=ex_rate, 
                exchanged_price=float(amount) * float(ex_rate), 
                method="Exchange"
            )
            history.save()

            # msg & redirect
            message = "You have successfuly exchanged your desired currencies!"
            success = True
        else:
            message = "You do not have a wallet with the specified currency!"
            success = False

    return Response({"message": message, "success": success, "ex_rate": ex_rate})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactions(request, walletIso, walletName, pageNum, numItems):
    pk             = request.user.pk
    counter        = 0

    acc            = Account.objects.get(pk=pk)
    branchAcc      = BranchAccounts.objects.filter(main_account__pk=pk)
    transactions   = TransactionHistory.objects.none()

    currency       = acc.main_currency

    # showing wallet's transactions
    if walletName != currency:
        # wallet's currency symbol
        currency_symbol = get_currency_symbol(walletName)

        # getting wallet's transactions
        for branch in branchAcc:
            person_history         = TransactionHistory.objects.filter(wallet=branch).filter(wallet__currency=walletName, wallet__iso2=walletIso).order_by('date').reverse()
            seconed_person_history = TransactionHistory.objects.filter(second_wallet=branch).filter(second_wallet__currency=walletName, second_wallet__iso2=walletIso).order_by('date').reverse()
            if person_history or seconed_person_history:
                transactions = person_history | seconed_person_history
    # showing account's transactions
    else:
        # account's currency symbol
        currency_symbol        = get_currency_symbol(currency)

        # getting account's transactions
        person_history         = TransactionHistory.objects.filter(person=acc).order_by('date').reverse()
        seconed_person_history = TransactionHistory.objects.filter(second_person=acc).order_by('date').reverse()
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
        person  = [item.person.created_by.username, item.person.main_currency] if item.person else "Anonymous"
        wallet  = [item.wallet.main_account.created_by.username, item.wallet.currency] if item.wallet else "Anonymous"
        person2 = item.second_person.created_by.username if item.second_person else "Anonymous"
        wallet2 = item.second_wallet.main_account.created_by.username if item.second_wallet else "Anonymous"

        newItem = {
            "id"        : id,
            "type"      : item.method,
            "price"     : item.price,
            "exPrice"   : item.exchanged_price,
            "date"      : [item.date.year, item.date.month, item.date.day, item.date.hour, item.date.minute, item.date.second],
            "person"    : person,
            "wallet"    : wallet,
            "person2"   : person2,
            "wallet2"   : wallet2,
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
    id = []
    transaction = TransactionHistory.objects.get(pk=tId)

    if transaction.person:
        currency = transaction.person.main_currency
        id.append(transaction.person.pk)
    if transaction.second_person:
        currency = transaction.second_person.main_currency
        id.append(transaction.second_person.pk)
    if transaction.wallet:
        currency = transaction.wallet.currency
        id.append(transaction.wallet.main_account.pk)
    if transaction.second_wallet:
        currency = transaction.second_wallet.currency
        id.append(transaction.second_wallet.main_account.pk)
    currency_symbol   = get_currency_symbol(currency)
    
    # if the transaction is a transfer
    if transaction.method == "Transfer":
        # user is giving money
        if transaction.wallet: # wallet was used
            if transaction.wallet.main_account.created_by == request.user:
                incoming = 0
                try:
                    transactor = transaction.second_person.created_by.username
                except:
                    try:
                        transactor = transaction.second_wallet.main_account.created_by.username
                    except AttributeError:
                        transactor = "Anonymous"
            else:
                incom = True
        elif transaction.person: # person was used
            # if user is sending money
            if transaction.person.created_by == request.user:
                incoming = 0
                try:
                    transactor = transaction.second_person.created_by.username
                except:
                    try:
                        transactor = transaction.second_wallet.main_account.created_by.username
                    except AttributeError:
                        transactor = "Anonymous"
            # if user is recieving
            else:
                incom = True
        else:
            incoming = 0
        # user is recieving moeny
        if incom == True:
            incoming = 1
            try:
                transactor  = transaction.person.created_by.username
            except:
                try:
                    transactor  = transaction.wallet.main_account.created_by.username
                except AttributeError:
                    transactor = "Anonymous"

    # if transaction is an exchange
    elif transaction.method == "Exchange":
        try:
            giver_symbol = get_currency_symbol(transaction.person.main_currency)
        except AttributeError:
            giver_symbol = get_currency_symbol(transaction.wallet.currency)
        try:
            reciever_symbol = get_currency_symbol(transaction.second_person.main_currency)
        except AttributeError:
            reciever_symbol = get_currency_symbol(transaction.second_wallet.currency)


    person  = [transaction.person.created_by.username, transaction.person.main_currency] if transaction.person else "Anonymous"
    wallet  = [transaction.wallet.main_account.created_by.username, transaction.wallet.currency] if transaction.wallet else "Anonymous"
    person2 = transaction.second_person.created_by.username if transaction.second_person else "Anonymous"
    wallet2 = transaction.second_wallet.main_account.created_by.username if transaction.second_wallet else "Anonymous"

    data = [{
        "type"          : transaction.method,
        "price"         : transaction.price,
        "exPrice"       : transaction.exchanged_price,
        "date"          : json.dumps(transaction.date.strftime('%Y-%m-%d %H:%M:%S %Z')),
        "message"       : transaction.purpose_of_use,
        "person"        : person,
        "wallet"        : wallet,
        "person2"       : person2,
        "wallet2"       : wallet2,
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
    friend_code     = ReferralCode.objects.filter(referral_code=enterd_code)
    user_currency_min = currency_min(currency)

    # creating a user
    user = CustomUser.objects.create(username=username, password=make_password(password), email=email, phone_number=phone_number, country=iso2,
    phone_ext=phone_ext, currency=currency, iso2=iso2, language=language)


    if friend_code.exists():  # referral code exists
        # getting current user's stuff
        user_currency_symbol    = get_currency_symbol(user.currency) # their currency symbol
        user_extra_bonus        = user_currency_min * EXTRA_BONUS_VALUE

        # creating an account for the user
        bonus = (user_currency_min * 1000) + user_extra_bonus
        Account.objects.create(created_by=user, bonus=bonus, total_balance=0, main_currency=currency, iso2=iso2, id=user.pk)

        # updating the user's bonus
        # Account.objects.filter(created_by=user).update(bonus = user_extra_bonus + user_currency_min * 1000)

        # getting the some info from the user whose referral code was used
        giver_user = ReferralCode.objects.get(referral_code=enterd_code).user # their name
        giver_account           = Account.objects.get(created_by=giver_user) # their account
        giver_balance           = giver_account.total_balance # their balance
        giver_bonus             = giver_account.bonus # their bonus
        giver_currency          = giver_account.main_currency # their currency in iso-3 format
        giver_currency_min      = currency_min(giver_currency) # $1 in their currency
        giver_extra_bonus       = giver_currency_min * EXTRA_BONUS_VALUE
        giver_currency_symbol   = get_currency_symbol(giver_currency) # their currency symbol

        # updating the giver user's bonus
        Account.objects.filter(created_by=giver_user).update(
            bonus = giver_bonus + giver_extra_bonus,
            total_balance = giver_balance + giver_currency_min
        )

        # send email to the person whose referral code was just used
        EMAIL_ID = config.get("EMAIL_ID")
        GIVER_EMAIL = giver_user.email
        send_mail(
            f"Dear {giver_user.username}!",
            f"{user['username']} just used your referral code! You recieved {giver_currency_symbol}{giver_currency_min} on your balance, and {giver_currency_symbol}{giver_extra_bonus} added to your bonus!",
            f"{EMAIL_ID}",
            [f"{GIVER_EMAIL}"],
        )

        # success message
        message = f"You have successfully registered, {user['username']}. For your prize, {user_currency_symbol}{user_extra_bonus} has been transfered to your bonus!"
    else:  # referral code not entered
        # creating an account for the user
        bonus = user_currency_min * 1000
        try:
            Account.objects.create(created_by=user, bonus=bonus, main_currency=currency, iso2=iso2, pk=user.pk)
        except Exception as e:
            print(e)
        # success message
        if enterd_code == "":  # referral code not submitted
            message = f"You have successfully registered, {username}!"
        else: # referral code was wrong
            message = f"Sorry, this referral code is incorrect, but you have successfully registered, {username}!"

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
