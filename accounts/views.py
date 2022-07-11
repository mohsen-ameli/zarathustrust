import json

from django.core.mail import send_mail, EmailMessage
from django.db.models import Q, F
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.models import CustomUser
from .functions import *
from .models import *
from .serializers import *


def loadConfig():
    with open('/etc/config.json') as config_file:
        return json.load(config_file)


@api_view(['GET'])
def jsonSearch(request, file):
    return Response(loadJson(file))


@permission_classes([IsAuthenticated])
def new_dunc(request):
    if request.user.id == 1:
        return Response("gg")
    else:
        return Response("How tf did u find this page ... smh ... script kiddies these days jeez")


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


# Referral Code
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inviteFriend(request):
    code = CustomUser.objects.get(pk=request.user.pk).referral_code
    return Response({"code" : code})


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
