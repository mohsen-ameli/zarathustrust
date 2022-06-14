import json
import os

from django.core.mail import send_mail, EmailMessage
from django.db.models import Q, F
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.functions import *
from accounts.models import *
from users.models import CustomUser
from wallets.models import BranchAccounts
from .serializers import *


def loadConfig():
    with open('/etc/config.json') as config_file:
        return json.load(config_file)


class AccountsApi(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    queryset = account.objects.all()


class InterestApi(viewsets.ModelViewSet):
    serializer_class = InterestSerializer
    queryset = account_interest.objects.all()


class UsersApi(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()


@api_view(['GET'])
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


@api_view(['POST'])
def deposit(request):
    pk              = request.user.pk
    config          = loadConfig()
    user            = CustomUser.objects.get(pk=pk)

    symbol          = request.data['symbol']
    amount          = request.data['amount']
    EMAIL_ID        = config.get('EMAIL_ID')
    EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')

    send_mail(f'DEPOSIT FOR {user.username}', 
            f'{user.username} with account number : {pk} has requested to deposit {symbol}{amount}',
            f'{EMAIL_ID}',
            [f'{EMAIL_ID_MAIN}'],)

    account.objects.filter(pk=pk).update(add_money=0)
    
    return Response()


@api_view(['POST'])
def withdraw(request):
    pk                  = request.user.pk
    config              = loadConfig()
    success             = False
    user                = CustomUser.objects.get(pk=pk)
    acc                 = account.objects.get(pk=pk)
    allBranchAcc        = BranchAccounts.objects.filter(main_account__pk=pk)

    moneyToWithdraw     = float(request.data['money'])
    currency            = request.data['currency']

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
        message = f"{userCurrencySymbol}{moneyToWithdraw} was requested to be taken out"
        success = True
    elif moneyToWithdraw > balance:
        message = "You have requested to take more than you have in your current balance !"
    else:
        message = f"Please consider that the minimum amount to withdraw must be {userCurrencySymbol}{minCurrency} or higher !"
        
    return Response({"message" : message, "success": success})


@api_view(['GET'])
def moneyForm(request):
    pk                  = request.user.pk
    acc                 = account.objects.get(pk=pk)
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
def wallets(request):
    pk              = request.user.pk
    acc             = account.objects.get(pk=pk)
    branchAccount   = BranchAccounts.objects.filter(main_account__pk=pk)

    wallets = user_wallets(branchAccount, acc)

    return Response(wallets)


@api_view(['POST'])
def walletsConfirm(request):
    pk       = request.user.pk
    currency = request.data['currency']
    iso2     = request.data['iso2']

    main_account = account.objects.get(pk=pk)
    BranchAccounts.objects.create(main_account=main_account, currency=currency, iso2=iso2)
    
    return Response()


@api_view(['POST'])
def transferSearch(request):
    typed = request.data['person']
    
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
def transferConfirm(request):
    # react variables
    config                   = loadConfig()
    pk                       = request.user.pk
    reciever_name            = request.data['reciever_name']
    purpose                  = request.data['purpose']
    moneyToSend              = request.data['moneyToSend']
    currency                 = request.data['currency']
    success                  = False

    # getting user's currency stuff
    currencyName             = currency.upper()
    userCurrencySymbol       = get_currency_symbol(currency.upper())
    minCurrency              = currency_min(currencyName)

    
    # Logic starts
    try:
        # getting giver/reciever stuff
        giver                    = account.objects.get(pk=pk)
        reciever                 = account.objects.get(created_by__username=reciever_name)
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
            giver_interest      = account_interest.objects.get(pk=pk)
            reciever_interest   = account_interest.objects.get(pk=reciever.pk)

            # if user has entered the bare minimum, and if has enough money
            if moneyToSend >= minCurrency and moneyToSend <= balance:

                ######## SETTING VARIABLES FOR THE UPDATE ########
                reciever_wallet     = BranchAccounts.objects.filter(main_account=reciever)
                reciever_specific   = reciever_wallet.filter(currency=currencyName)
                # reciever and giver's accounts do not have the same currency
                if giver_currency == currencyName: # account-to-somthing
                    giver_total_balance = balance
                    giver_update = account.objects.filter(pk=pk)
                    if reciever_specific.exists():
                        # account-to-wallet
                        print("account-to-wallet")

                        reciever_total_balance = reciever_specific.values("total_balance")[0]['total_balance']
                        reciever_update = reciever_specific
                        update_interest_rate = False

                        # recording the transaction
                        r = transaction_history(person=giver, second_wallet=reciever_specific.get(main_account=reciever),
                        price=moneyToSend, purpose_of_use=purpose, method="Transfer")
                    elif giver_currency == reciever_currency and currencyName:
                        # account-to-account
                        print("account-to-account")

                        reciever_total_balance = reciever.total_balance
                        reciever_update = account.objects.filter(created_by__username=reciever_name)
                        update_interest_rate = True

                        # recording the transaction
                        r = transaction_history(person=giver, second_person=reciever,
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
                        r = transaction_history(person=giver, second_wallet=new,
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
                        r = transaction_history(wallet=abc, second_wallet=reciever_wallet.get(currency=currencyName),
                        price=moneyToSend, purpose_of_use=purpose, method="Transfer")
                    elif reciever.main_currency == currencyName:
                        # wallet-to-account
                        print("wallet-to-account")
                        reciever_total_balance = reciever.total_balance
                        reciever_update = account.objects.filter(created_by__username=reciever_name)
                        update_interest_rate = True

                        # recording the transaction
                        r = transaction_history(wallet=abc, second_person=reciever,
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
                        r = transaction_history(wallet=abc, second_wallet=new,
                        price=moneyToSend, purpose_of_use=purpose, method="Transfer")
                
                ######## UPDATING ########
                # adding money to reciever
                new_total_balance = reciever_total_balance + moneyToSend
                # updating the reciever
                reciever_update.update(total_balance=new_total_balance)
                # taking money from giver
                rmv_total_balance = giver_total_balance - moneyToSend
                # updating the giver
                giver_update.update(total_balance=rmv_total_balance)

                ######## UPDATE ACCOUNT INTEREST ########
                if update_interest_rate is True:
                    # updaing account interest
                    reciever_interest.interest = F('interest') + moneyToSend
                    reciever_interest.save()
                # taking money from giver
                b = giver_interest.interest - moneyToSend
                # updating giver
                account_interest.objects.filter(pk=pk).update(interest=b)



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
                message = f"Please consider that the minimum amount to send is {userCurrencySymbol}{minCurrency} !"
            elif moneyToSend > balance:
                message = "You have requested to transfer more than you have in your current balance !"
        else:
            message = "You cannot send money to yourself."
    except ObjectDoesNotExist:
        message = "The account you are trying to send money to has not finished signing up !"

    return Response({"message" : message, "success": success})


@api_view(['POST', 'GET'])
def currencyEx(request, fromCurr, fromIso, amount, toCurr, toIso):
    pk                  = request.user.pk
    message             = ""
    success             = True
    notEnough           = False
    toCurr              = toCurr.upper()
    fromCurr            = fromCurr.upper()

    wallet              = BranchAccounts.objects.filter(main_account__pk=pk)
    accInterest         = account_interest.objects.get(pk=pk)
    acc                 = account.objects.get(pk=pk)

    minTo               = currency_min(toCurr)
    minFrom             = currency_min(fromCurr)

    #-------------------------------- CHECKS ------------------------------#
    # confirming from and to currencies
    if minTo is None or minFrom is None: # the currency doesnt exist (JXL)
        message = "88You cannot exchange with the specified currencies !"
        return Response({"message": message, "success": False})
    elif fromCurr == toCurr: # exchanging the same currencies
        message = "You cannot exchange the same currencies !"
        return Response({"message": message, "success": False})
    elif not wallet.filter(currency=toCurr, iso2=toIso).exists() and acc.main_currency != toCurr:
        message = "You do not own the specified wallets !"
        return Response({"message": message, "success": False})
    elif not wallet.filter(currency=fromCurr, iso2=fromIso).exists() and acc.main_currency != fromCurr:
        message = "You do not own the specified wallets !"
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
        message = "You do not have enough money for this transaction !"
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
                history = transaction_history(
                    person=acc, 
                    second_wallet=wallet.get(currency=toCurr, iso2=toIso), 
                    price=float(amount), 
                    ex_rate=ex_rate, 
                    exchanged_price=float(amount) * float(ex_rate), 
                    method="Exchange"
                )
            # sending from another wallet to wallet
            else:
                history = transaction_history(
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
            message = "You have successfuly exchanged your desired currencies !"
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
            history = transaction_history(
                wallet=wallet.get(currency=fromCurr, iso2=fromIso), 
                second_person=acc, 
                price=float(amount), 
                ex_rate=ex_rate, 
                exchanged_price=float(amount) * float(ex_rate), 
                method="Exchange"
            )
            history.save()

            # msg & redirect
            message = "You have successfuly exchanged your desired currencies !"
            success = True
        else:
            message = "You do not have a wallet with the specified currency !"
            success = False

    return Response({"message": message, "success": success, "ex_rate": ex_rate})


@api_view(['GET'])
def transactions(request, walletIso, walletName, pageNum, numItems):
    pk             = request.user.pk
    counter        = 0

    acc            = account.objects.get(pk=pk)
    branchAcc      = BranchAccounts.objects.filter(main_account__pk=pk)
    transactions   = transaction_history.objects.none()

    currency       = acc.main_currency

    # showing wallet's transactions
    if walletName != currency:
        # wallet's currency symbol
        currency_symbol = get_currency_symbol(walletName)

        # getting wallet's transactions
        for branch in branchAcc:
            person_history         = transaction_history.objects.filter(wallet=branch).filter(wallet__currency=walletName, wallet__iso2=walletIso).order_by('date').reverse()
            seconed_person_history = transaction_history.objects.filter(second_wallet=branch).filter(second_wallet__currency=walletName, second_wallet__iso2=walletIso).order_by('date').reverse()
            if person_history or seconed_person_history:
                transactions = person_history | seconed_person_history
    # showing account's transactions
    else:
        # account's currency symbol
        currency_symbol        = get_currency_symbol(currency)

        # getting account's transactions
        person_history         = transaction_history.objects.filter(person=acc).order_by('date').reverse()
        seconed_person_history = transaction_history.objects.filter(second_person=acc).order_by('date').reverse()
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
def transactionDetail(request, tId):
    pk  = request.user.pk
    incoming = 0
    transactor = None
    incom = False
    giver_symbol = None
    reciever_symbol = None
    id = []
    allowed = False
    transaction = transaction_history.objects.get(pk=tId)

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


