import os
import decimal
import json
from django.db.models.expressions import Exists
import requests

from django.http.response import JsonResponse
from ipware import get_client_ip
from crum import get_current_user

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.core.exceptions import PermissionDenied
from django.db.models import Q, F
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.utils.translation import gettext as _
from django.utils import translation
from users.models import CustomUser
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from .forms import AddMoneyForm, TakeMoneyForm, TransferSendForm
from .models import account, account_interest, transaction_history
from .tasks import interest_loop
from .functions import *
from users.models import ReferralCode
from wallets.models import BranchAccounts

with open('/etc/config.json') as config_file:
    config = json.load(config_file)


################ Views ################

# Admin Page
def AdminRickRoll(lmfao):
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley") 


# Landing Page
def LandingPageView(request):
    ip, is_routable = get_client_ip(request)
    if ip is None:
        code = None
    else:
        if is_routable:
            url = f"https://geolocation-db.com/json/{ip}&position=true"
            response = requests.get(url).json()
            code = response['country_code']
        else:
            code = None

    country = code
    if country is None:
        lang = 'en'
    else:
        country_code = country.upper()
        # project = os.path.abspath(os.path.dirname(__name__)) # root of django project
        project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file = f'{project}/json/country_languages.json' # getting the file containing all country codes
        with open(file, 'r') as config_file: # opening and reading the json file
            data = json.load(config_file)
        langs = data[country_code] # searching for our specific country code
        lang = next(iter(langs))
    translation.activate(lang)
    response = render(request, 'accounts/landing_page.html')
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
    return response


# About Page
def AboutTemplateView(request):
    context = {'stuff' : _('hello hello hi hi')}
    return render(request, 'accounts/about.html', context)


# Celery hard start
@login_required
def new_dunc(request):
    if request.user.id == 1:
        # # # celery -A money_moe worker -l info --pool=solo
        interest_loop.delay()
        return render(request, 'accounts/new_dunc.html')
    else:
        return HttpResponse("<h1>How tf did u find this page ... smh ... script kiddies these days jeez</h1>")


# Home Page
@login_required
def HomeView(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()
    acc         = account.objects.get(pk=pk) # user's account
    user_       = CustomUser.objects.get(pk=pk) # user's model
    currency    = get_currency_symbol(user_.currency) # user model's currency
    branch_acc  = BranchAccounts.objects.filter(main_account__pk=pk) # getting user's wallets

    # loading data
    data = country_currencies_clean()

    # if user selected a country
    wallet_name = request.GET.get("wallet-name")

    # getting user's wallets
    wallets = user_wallets(request, wallet_name, branch_acc, user_, acc)

    # setting some vars for context
    if wallet_name:
        wallet_name = wallet_name.upper()
        # testing to see if the entered GET arg actually exists in the user's wallet currency column
        test = branch_acc.filter(currency=wallet_name).exists()
        if test is not False or user_.currency == wallet_name:
            # setting variables for our context
            for i in data:
                if data[i] == wallet_name:
                    wallet_iso       = i
                    wallet_currency  = data[i]
                    wallet_symbol    = get_currency_symbol(data[i])
                    try:
                        wallet_balance   = branch_acc.get(currency=data[i]).total_balance
                    except:
                        wallet_balance = acc.total_balance
        else:
            wallet_name = None
    else: # default view of the user's account
        # show users their default wallet
        for i in data:
            if data[i] == acc.main_currency:
                wallet_iso       = i
                wallet_currency  = data[i]
                wallet_symbol    = get_currency_symbol(data[i])
                wallet_balance   = acc.total_balance

    context = {
        'interest_list'         : account_interest.objects.get(pk=pk),
        'object'                : acc,
        'is_bus'                : user_.is_business,
        'currency'              : currency,

        'wallet_iso'            : wallet_iso,
        'wallet_currency'       : wallet_currency,
        'wallet_symbol'         : wallet_symbol,
        'wallet_balance'        : wallet_balance,
        'wallets'               : zip(wallets),
        'wallets_count'         : len(wallets),
    }
    return render(request, 'accounts/home.html', context)


# Settings
@login_required
def Settings(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()

    context = {
        "pk" : pk
    }
    return render(request, "accounts/settings.html", context)


# Settings Country search
@login_required
def SettingsCountry(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()

    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/country_names.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)

    all_countries = data.items()
    context = {
        "countries" : all_countries,
        "data" : data
    }
    return render(request, "accounts/settings_country.html", context)


# Settings Country Confirm
@login_required
def SettingsCountryConfirm(request, pk, country):
    if not correct_user(pk):
        raise PermissionDenied()

    if request.method == "POST":
        CustomUser.objects.filter(pk=pk).update(country=country)
        messages.success(request, _("You have successfully updated your country !"))
        return redirect('accounts:home', pk=pk)
    context = {
        "country" : country
    }
    return render(request, "accounts/settings_country_confirm.html", context)


# Money Send Sending
@login_required
def TransferSendView(request, pk, reciever_name):
    if not correct_user(pk):
        raise PermissionDenied()
    # getting user's currency stuff
    User                = CustomUser.objects.get(pk=request.user.pk)
    currency_name       = User.currency
    currency_symbol_    = get_currency_symbol(currency_name)
    min_currency        = currency_min(currency_name)

    # getting giver/reciever stuff
    giver                    = account.objects.get(pk=pk)
    reciever                 = account.objects.get(created_by__username=reciever_name)
    giver_wallet             = BranchAccounts.objects.filter(main_account=giver)
    balance                  = giver.total_balance
    giver_currency           = giver.main_currency
    reciever_currency        = reciever.main_currency

    # making the array for currency options
    currency_options    = [(currency_name, currency_symbol_)]
    if request.GET.get("currency"):
        currency_GET        = request.GET.get("currency").upper()
        # testing to see if the entered GET arg actually exists in the user's wallet currency column
        test = BranchAccounts.objects.filter(main_account__pk=pk).filter(currency=currency_GET).exists()
        if test is not False:
            currency_symbol_    = get_currency_symbol(currency_GET)
            currency_name       = currency_GET
            min_currency        = currency_min(currency_name)
            balance             = giver_wallet.get(currency=currency_GET).total_balance
    
    branch_acc = BranchAccounts.objects.filter(main_account__pk=pk)
    for wallet in branch_acc:
        currency_options.append((wallet.currency, get_currency_symbol(wallet.currency)))
    
    if request.method == "POST":
        form = TransferSendForm(request.POST)
        if form.is_valid():
            # Logic starts
            try:
                if giver != reciever: # making sure the user isn't sending money to themselves
                    giver_interest      = account_interest.objects.get(pk=pk)
                    reciever_interest   = account_interest.objects.get(pk=reciever.pk)

                    # form variables
                    purpose     = form.cleaned_data.get("purpose")
                    MoneyToSend = form.cleaned_data.get("money_to_send")

                    # if user has entered the bare minimum, and if has enough money
                    if MoneyToSend >= min_currency and MoneyToSend <= balance:

                        ######## SETTING VARIABLES FOR THE UPDATE ########
                        reciever_wallet = BranchAccounts.objects.filter(main_account=reciever)
                        reciever_specific = reciever_wallet.filter(currency=currency_name)
                        # reciever and giver's accounts do not have the same currency
                        if giver_currency == currency_name: # account-to-somthing
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
                                price=MoneyToSend, purpose_of_use=purpose, method="Transfer")
                            elif giver_currency == reciever_currency and currency_name:
                                # account-to-account
                                print("account-to-account")

                                reciever_total_balance = reciever.total_balance
                                reciever_update = account.objects.filter(created_by__username=reciever_name)
                                update_interest_rate = True

                                # recording the transaction
                                r = transaction_history(person=giver, second_person=reciever,
                                price=MoneyToSend, purpose_of_use=purpose, method="Transfer")
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
                                price=MoneyToSend, purpose_of_use=purpose, method="Transfer")
                        else: # wallet-to-something
                            giver_total_balance = giver_wallet.filter(currency=currency_name).values("total_balance")[0]['total_balance']
                            giver_update = giver_wallet.filter(currency=currency_name)
                            abc = giver_wallet.get(currency=currency_name)
                            if reciever_specific.exists():
                                # wallet-to-wallet
                                print("wallet-to-wallet")
                                reciever_total_balance = reciever_specific.values("total_balance")[0]['total_balance']
                                reciever_update = reciever_specific
                                update_interest_rate = False

                                # recording the transaction
                                r = transaction_history(wallet=abc, second_wallet=reciever_wallet.get(currency=currency_name),
                                price=MoneyToSend, purpose_of_use=purpose, method="Transfer")
                            elif reciever.main_currency == currency_name:
                                # wallet-to-account
                                print("wallet-to-account")
                                reciever_total_balance = reciever.total_balance
                                reciever_update = account.objects.filter(created_by__username=reciever_name)
                                update_interest_rate = True

                                # recording the transaction
                                r = transaction_history(wallet=abc, second_person=reciever,
                                price=MoneyToSend, purpose_of_use=purpose, method="Transfer")
                            else:
                                # wallet-to-newWallet
                                print("wallet-to-newWallet")
                                # creating a new wallet for reciever
                                new = BranchAccounts(main_account=reciever, currency=currency_name)
                                new.save()
                                reciever_total_balance = 0
                                reciever_update = BranchAccounts.objects.filter(main_account=reciever)
                                update_interest_rate = False
                                
                                # recording the transaction
                                r = transaction_history(wallet=abc, second_wallet=new,
                                price=MoneyToSend, purpose_of_use=purpose, method="Transfer")
                        
                        ######## UPDATING ########
                        # adding money to reciever
                        new_total_balance = reciever_total_balance + MoneyToSend
                        # updating the reciever
                        reciever_update.update(total_balance=new_total_balance)
                        # taking money from giver
                        rmv_total_balance = giver_total_balance - MoneyToSend
                        # updating the giver
                        giver_update.update(total_balance=rmv_total_balance)

                        ######## UPDATE ACCOUNT INTEREST ########
                        if update_interest_rate is True:
                            # updaing account interest
                            reciever_interest.interest = F('interest') + MoneyToSend
                            reciever_interest.save()
                        # taking money from giver
                        b = giver_interest.interest - MoneyToSend
                        # updating giver
                        account_interest.objects.filter(pk=pk).update(interest=b)



                        # success message
                        messages.success(request, _(f'{currency_symbol_}{MoneyToSend} has been transfered to {reciever_name}'))

                        # emailing the reciever
                        reciever_email = CustomUser.objects.get(pk=reciever.pk).email
                        giver_username = CustomUser.objects.get(pk=pk).username
                        giver_email = CustomUser.objects.get(pk=pk).email
                        EMAIL_ID       = config.get('EMAIL_ID')
                        msg = EmailMessage(_("ZARATHUSTRUST MONEY TRANSFER"),
                                _(f"Dear {reciever_name}, <br> {giver_username} just transfered {currency_symbol_}{round(MoneyToSend, 1)} to your account ! <br> Purpose of Use : {purpose}"),
                                f"{EMAIL_ID}",
                                [f"{reciever_email}"]
                        )
                        msg.content_subtype = "html"
                        msg.send()

                        # emailing the giver
                        msg1 = EmailMessage(_("ZARATHUSTRUST MONEY TRANSFER"),
                                _(f"Dear {giver_username}, <br> {currency_symbol_}{round(MoneyToSend, 1)} has been transfered to {reciever_name} successfully ! <br> Purpose of Use : {purpose}"),
                                f"{EMAIL_ID}",
                                [f"{giver_email}"]
                        )
                        msg1.content_subtype = "html"
                        msg1.send()

                        # add the transaction to the user's history
                        r.save()

                        return redirect(reverse('accounts:home', kwargs={'pk':pk}))
                    elif MoneyToSend < min_currency:
                        messages.warning(request, _(f'Please consider that the minimum amount to send is {currency_symbol_}{min_currency} !'))
                    elif MoneyToSend > balance:
                        messages.warning(request, _(f'You have requested to transfer more than you have in your current balance !'))
                else:
                    messages.warning(request, _(f'You cannot send money to yourself.'))
            except ObjectDoesNotExist as e:
                messages.warning(request, _(f'The account you are trying to send money to has not finished signing up !'))
    else:
        form = TransferSendForm()
    
    context = {
        'form'                  : form,
        'reciever_name'         : reciever_name,
        'user_currency_symbol'  : currency_symbol_,
        'currency'              : currency_name,
        'min_currency'          : min_currency,
        'currency_options'      : currency_options,
    }
    return render(request, "accounts/transfer_send.html", context)


# Money Send Searching
@login_required
def TransferSearchView(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()

    return render(request, "accounts/transfer_search.html")


# Transfer Searching Results
def search_results(request):
    if request.is_ajax():
        # getting the stuff that was typed in in transfer.html
        typed = request.POST.get('person')
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
            res = _("No accounts were found.")
        return JsonResponse({'data' : res})
    return JsonResponse({})


# Cash Out
@login_required
def CashOut(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()
    
    # getting user's currency stuff
    user_ = CustomUser.objects.get(pk=request.user.pk)
    currency = get_currency_symbol(user_.currency)
    
    interest_rate     = account_interest.objects.get(pk=pk).interest_rate
    guy               = account.objects.get(pk=pk)
    bonus             = guy.bonus
    if interest_rate >= 0.1:
        # checking bonus if it's more than interest rate or not
        if interest_rate <= bonus:
            total_balance = account.objects.get(pk=pk).total_balance # getting total balance
            total_balance = total_balance + (round(interest_rate, 1) * 2) 
            account.objects.filter(pk=pk).update(total_balance=total_balance) # updating total balance
            account_interest.objects.filter(pk=pk).update(interest=total_balance) # updating account interest
            messages.success(request, _(f'You have successfully cashed out {currency}{round(interest_rate, 1) * 2}'))
            account_interest.objects.filter(pk=pk).update(interest_rate=0)
            account.objects.filter(pk=pk).update(bonus=bonus-round(interest_rate, 1)) # updating bonus
            r = transaction_history(person=guy, price=round(interest_rate, 1) * 2, method="Cash Out")
            r.save()
            return redirect('accounts:home', pk=pk)
        else:
            total_balance = account.objects.get(pk=pk).total_balance # getting total balance
            total_balance = total_balance + bonus + interest_rate
            account.objects.filter(pk=pk).update(total_balance=total_balance) # updating total balance
            account_interest.objects.filter(pk=pk).update(interest=total_balance) # updating account interest
            messages.success(request, _(f'You have successfully cashed out {currency}{round(interest_rate, 1) + bonus}'))
            account_interest.objects.filter(pk=pk).update(interest_rate=0)
            account.objects.filter(pk=pk).update(bonus=0) # updating bonus 
            r = transaction_history(person=guy, price=round(interest_rate, 1) + bonus, method="Cash Out")
            r.save()
            return redirect('accounts:home', pk=pk)
    elif interest_rate < 0.1:
        messages.warning(request, _(f'You need at least $0.1 to be able to cash out ! keep going tho'))
        return redirect('accounts:home', pk=pk)


# Referral Code
@login_required
def ReferralCodeView(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()
    
    a = ReferralCode.objects.get(user=request.user).referral_code
    return render(request, 'accounts/referral_code.html', {"referral_code" : a})


# Add Money Form
@login_required
def DepositUpdateView(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()

    # getting user's currency stuff
    user_               = CustomUser.objects.get(pk=request.user.pk)

    # redirecting to new card if user doesn't have a card
    if user_.stripe_id is None:
        return redirect("wallets:new-card", pk=pk)

    currency_name       = user_.currency
    currency_symbol_    = get_currency_symbol(currency_name)
    min_currency        = currency_min(currency_name)
    currency_options    = [(currency_name, currency_symbol_)] # currencies that will be showed as options

    if request.GET.get("currency"):
        currency_GET        = request.GET.get("currency").upper()
        # testing to see if the entered GET arg actually exists in the user's wallet currency column
        test = BranchAccounts.objects.filter(main_account__pk=pk).filter(currency=currency_GET).exists()
        if test is not False:
            currency_symbol_    = get_currency_symbol(currency_GET)
            currency_name       = currency_GET
            min_currency        = currency_min(currency_name)

    branch_acc = BranchAccounts.objects.filter(main_account__pk=pk)
    for wallet in branch_acc:
        currency_options.append((wallet.currency, get_currency_symbol(wallet.currency)))


    form = AddMoneyForm(request.POST or None)
    if form.is_valid():
        add_money           = form.cleaned_data.get('add_money')
        if add_money >= min_currency:
            EMAIL_ID        = config.get('EMAIL_ID')
            EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')
            send_mail(f'{get_current_user()}', 
                    f'{get_current_user()} with account number : {pk} has requested to deposit {currency_symbol_}{add_money}',
                    f'{EMAIL_ID}',
                    [f'{EMAIL_ID_MAIN}'],)
            account.objects.filter(pk=pk).update(add_money=0)
            # messages.success(request, _(f"${add_money} was requested to be put into your account"))
            return redirect('accounts:add-money-info', pk=pk)
        else:
            messages.warning(request, _(f"Please consider that the minimum amount to withdraw must be {currency_symbol_}{min_currency} or higher !"))
            return redirect('accounts:add-money', pk=pk)
    
    context = {
        'form'                  : form, 
        'min_currency'          : min_currency,
        'currency'              : currency_name,
        'user_currency_symbol'  : currency_symbol_,
        'currency_options'      : currency_options,
    }
    return render(request, 'accounts/add_money_form.html', context)


# Add Money Info
@login_required
def DepositInfo(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()
        
    return render(request, 'accounts/add_money_info.html')


# Take Money Form
@login_required
def WithdrawUpdateView(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()
    
    # some vars
    user_               = CustomUser.objects.get(pk=request.user.pk)

    # redirecting to new card if user doesn't have a card
    if user_.stripe_id is None:
        return redirect("wallets:new-card", pk=pk)

    acc                 = account.objects.get(pk=pk)
    branch_acc          = BranchAccounts.objects.filter(main_account__pk=pk)
    currency_name       = user_.currency
    balance             = acc.total_balance
    currency_symbol_    = get_currency_symbol(currency_name)
    min_currency        = currency_min(currency_name)

    # currencies that will be showed as options
    currency_options    = [(currency_name, currency_symbol_)]

    currency_GET        = request.GET.get("currency")
    if currency_GET:
        currency_GET    = currency_GET.upper()
        # testing to see if the entered GET arg actually exists in the user's wallet currency column
        test = BranchAccounts.objects.filter(main_account__pk=pk).filter(currency=currency_GET).exists()
        if test is not False:
            currency_symbol_    = get_currency_symbol(currency_GET)
            currency_name       = currency_GET
            min_currency        = currency_min(currency_name)
            balance             = branch_acc.get(currency=currency_GET).total_balance

    for wallet in branch_acc:
        currency_options.append((wallet.currency, get_currency_symbol(wallet.currency)))

    form                    = TakeMoneyForm(request.POST or None)
    if form.is_valid():
        take_money          = form.cleaned_data.get('take_money')
        if take_money >= min_currency and take_money <= balance:

            # sending email to the admins
            EMAIL_ID        = config.get('EMAIL_ID')
            EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')
            MOE_EMAIL       = config.get('MOE_EMAIL')
            send_mail(f'Withdraw for {user_.username}', 
                    f'{user_.username} with account number "{pk}" has requested to withdraw {currency_symbol_}{take_money}',
                    f'{EMAIL_ID}',
                    [f'{EMAIL_ID_MAIN}'],)
                    
            # updating user's account
            if currency_GET:
                acc = BranchAccounts.objects.filter(main_account=acc).get(currency=currency_GET)
            acc.take_money = 0
            acc.total_balance = F('total_balance') - take_money
            acc.save()

            messages.success(request, _(f"{currency_symbol_}{take_money} was requested to be taken out"))
            return redirect('accounts:home', pk=pk)
        elif take_money > balance:
            messages.warning(request, _("You have requested to take more than you have in your current balance !"))
        else:
            messages.warning(request, _(f"Please consider that the minimum amount to withdraw must be {currency_symbol_}{min_currency} or higher !"))
    
    context = {
        'form'                  : form,
        'min_currency'          : min_currency,
        'currency'              : currency_name,
        'user_currency_symbol'  : currency_symbol_,
        'user_currency_symbol'  : currency_symbol_,
        'currency_options'      : currency_options
    }
    return render(request, 'accounts/take_money_form.html', context)



# Checkout Page
@login_required
def checkout(request, shop, price):
    pk = request.user.pk
    if not correct_user(pk):
        raise PermissionDenied()

    if "$" in price:
        price = price.replace("$", '')
    total_balance = account.objects.get(created_by=request.user).total_balance
    remaining     = round(total_balance - decimal.Decimal(float(price)), 2)
    buyer_balance = account.objects.get(pk=get_current_user().pk).total_balance
    currency = CustomUser.objects.get(pk=pk).currency
    context = {'pk' : pk,'price' : price, 'balance' : total_balance, 'remaining' : remaining, 'shop' : shop, 'currency' : currency}

    while "," in price:
        translation_table = dict.fromkeys(map(ord, ','), None)
        price = price.translate(translation_table)
    price = decimal.Decimal(float(price)) # compatibilizing str price to decimalField in models 
    if request.method == "POST":
        if buyer_balance >= round(price, 2):
            shop_balance = account.objects.get(created_by__username=shop).total_balance
            # adding price to the shop owner
            account.objects.filter(created_by__username=shop).update(total_balance=shop_balance + price)
            # subtracting price from buyer
            account.objects.filter(pk=get_current_user().pk).update(total_balance=buyer_balance - price)

            # add the transaction to the user's history
            person = account.objects.get(pk=get_current_user().pk)
            second_person = account.objects.get(created_by__username=shop)
            r = transaction_history(person=person, second_person=second_person,
            price=price, method="Payment")
            r.save()

            # messages.success(request, _("Your order was purchased successfully !"))
            return HttpResponse('<script type="text/javascript">window.close();</script>')
            # return redirect(reverse("accounts:home", kwargs={"pk" : get_current_user().pk}))
        else:
            messages.warning(request, _("You do not have enough money for this order !"))
            return redirect(reverse("accounts:add-money", kwargs={"pk" : get_current_user().pk}))

    return render(request, "accounts/checkout.html", context)


# History Page
@login_required
def History(request, pk):
    if not correct_user(pk):
        raise PermissionDenied()

    # getting user's currency stuff
    user_                  = CustomUser.objects.get(pk=pk)
    currency               = account.objects.get(pk=pk).main_currency
    acc                    = account.objects.get(pk=pk)
    branch_acc             = BranchAccounts.objects.filter(main_account__pk=pk) # getting user's wallets

    counter = 0
    transactions = transaction_history.objects.none()
    # if user has selected a wallet
    wallet = request.GET.get("wallet-name")

    # getting user's wallets
    wallets = user_wallets(request, wallet, branch_acc, user_, acc)

    # checking if user selected to see their wallets and only wallets
    if wallet and wallet != currency:
        test = branch_acc.filter(currency=wallet).exists()
        if test is not False or user_.currency == wallet:
            # wallet's currency symbol
            currency_symbol = get_currency_symbol(wallet)

            # getting wallet's transactions
            for branch in branch_acc:
                person_history         = transaction_history.objects.filter(wallet=branch).filter(wallet__currency=wallet).order_by('date').reverse()
                seconed_person_history = transaction_history.objects.filter(second_wallet=branch).filter(second_wallet__currency=wallet).order_by('date').reverse()
                if person_history or seconed_person_history:
                    transactions = person_history | seconed_person_history
                    counter = Paginator(transactions, 1).count
        else:
            return redirect('accounts:history', pk=pk)
    else: # normal account history
        wallet = currency
        # user's account's currency symbol
        currency_symbol        = get_currency_symbol(currency)

        # getting account's transactions
        person_history         = transaction_history.objects.filter(person=acc).order_by('date').reverse()
        seconed_person_history = transaction_history.objects.filter(second_person=acc).order_by('date').reverse()
        transactions = person_history | seconed_person_history
        counter = Paginator(transactions, 1).count

    if request.GET.get("num"):
        pagination_number = request.GET.get('num') or 10
        if request.GET.get('num') == "all":
            pagination_number = counter
        paginator   = Paginator(transactions, pagination_number)
        page_number = request.GET.get('page')
        page_obj    = paginator.get_page(page_number)

        context = {
            "page_obj"             : page_obj,
            "currency"             : currency,
            "pagination_number"    : pagination_number,
            "wallet"               : wallet,
            "counter"              : counter,
            "currency_symbol"      : currency_symbol,
            "wallets"              : zip(wallets),
        }
    else:
        paginator   = Paginator(transactions, 10)
        page_number = request.GET.get('page')
        page_obj    = paginator.get_page(page_number)

        context = {
            "page_obj"             : page_obj, 
            "currency"             : currency, 
            "pagination_number"    : 10,
            "wallet"               : wallet,
            "counter"              : counter,
            "currency_symbol"      : currency_symbol,
            "wallets"              : zip(wallets),
        }
    return render(request, "accounts/history.html", context)


# History Detail Page
@login_required
def HistoryDetail(request, pk, tran_id):
    if not correct_user(pk):
        raise PermissionDenied()

    incoming = 0
    transactor = None
    incom = False
    giver_symbol = None
    reciever_symbol = None
    id = []
    allowed = False
    transaction = transaction_history.objects.get(pk=tran_id)

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
                    transactor = transaction.second_wallet.main_account.created_by.username
            else:
                incom = True
        elif transaction.person: # person was used
            # if user is sending money
            if transaction.person.created_by == request.user:
                incoming = 0
                try:
                    transactor = transaction.second_person.created_by.username
                except:
                    transactor = transaction.second_wallet.main_account.created_by.username
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
                transactor  = transaction.wallet.main_account.created_by.username

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

    context = {
        "transaction"       : transaction,
        "currency_symbol"   : currency_symbol,
        "incoming"          : incoming,
        "transactor"        : transactor,
        "giver_symbol"      : giver_symbol,
        "reciever_symbol"   : reciever_symbol,
    }

    # whether or not user's viewing the details of their own transactions
    for i in id:
        if i == pk:
            allowed = True
            
    if allowed:
        return render(request, "accounts/history_detail.html", context)
    else: 
        raise PermissionDenied()



'''# DELETE this later
def payment(request, url1, url2, url3, url4):
    # www.amazon.ca/CYBERPOWERPC-Xtreme-i5-10400F-GeForce-GXiVR8060A10/dp/B08FBK2DK5/
    # www.newegg.ca/abs-ali521/p/N82E16883360126/
    if request.user.is_authenticated:


        header = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "Accept-Language" : "en"
        }
        url = f"https://{url1}/{url2}/{url3}/{url4}"
        r = requests.get(url, headers=header)

        if "amazon" in url1:
            soup = BeautifulSoup(r.text, "lxml")
            try:
                price = soup.select_one('#price_inside_buybox').getText().strip()
            except AttributeError:
                price = soup.select_one('#priceblock_ourprice').getText().strip()
            if '$' not in price:
                price = price[:-1]
                price = price.replace(",", ".")
            else:
                price = price[1:]
        elif "newegg" in url1:
            soup = BeautifulSoup(r.content, "lxml")
            price = soup.select_one('.price-current').getText()
            price = price[1:]

        total_balance = account.objects.get(created_by=request.user).total_balance
        translation_table = dict.fromkeys(map(ord, ','), None)
        price = price.translate(translation_table)
        remaining     = round(total_balance - decimal.Decimal(float(price)), 2)

        return render(request, 'accounts/payment.html', 
            {"url1" : url1, "url2" : url2, "url3" : url3, "url4" : url4, 
            "price" : price, "total" : total_balance, "remaining" : remaining})
    else:
        return redirect(reverse("login-view-pay", kwargs={"url1" : url1, "url2" : url2, "url3" : url3, "url4" : url4}))
# DELETE this later
def paying_func(shop, price, buyer_balance):
    shop_owner = account.objects.get(created_by__username=shop).created_by
    shop_balance = account.objects.get(created_by=shop_owner).total_balance
    new_balance = shop_balance + price
    account.objects.filter(created_by=shop_owner).update(total_balance = new_balance)

    # subtracting the price from the buyer
    account.objects.filter(pk=get_current_user().pk).update(total_balance=buyer_balance-price)
# DELETE this later
@login_required
def payment_done(request, url1, url2, url3, url4, price):
    while "," in price:
        translation_table = dict.fromkeys(map(ord, ','), None)
        price = price.translate(translation_table)
    price = decimal.Decimal(float(price)) # compatibilizing str price to decimalField in models 

    # Checking to see if the buyer has enough money
    buyer_balance = account.objects.get(pk=get_current_user().pk).total_balance
    if buyer_balance >= round(price, 2):
        # adding the price to the shop owner
        if "amazon" in url1:
            paying_func("amazon", price, buyer_balance)
        elif "newegg" in url1:
            paying_func("newegg", price, buyer_balance)
        messages.success(request, _("Your order was purchased successfully !"))
        return redirect(reverse("accounts:home", kwargs={"pk" : get_current_user().pk}))
    else:
        messages.warning(request, _("You do not have enough money for this order !"))
        return redirect(request.META['HTTP_REFERER']) '''


'''# Class Based Views
class HomeView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = account
    template_name = 'accounts/home.html'

    def test_func(self):
        account = self.get_object()
        if self.request.user == account.created_by:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['interest_list'] = account_interest.objects.get(pk=get_current_user().pk)
        context['is_bus'] = CustomUser.objects.get(pk=get_current_user().pk).is_business
        context['currency'] = CustomUser.objects.get(pk=get_current_user().pk).currency

        acc = account.objects.get(pk=get_current_user().pk)

        url = f'https://api.exchangerate.host/convert?from=USD&to=EUR' # 1 USD to EUR
        response = requests.get(url) # getting a response
        data = response.json() # getting the data
        euro_rate = data['result'] # extracting the desired column and converting it into Decimal django field
        context['euro_balance'] = round(decimal.Decimal(euro_rate) * acc.total_balance, 2) # set the EUR balance to euro_balance for templates
        context['euro_rate']    = euro_rate  # passing euro_rate for 1 USD
        context['euro_bonus']   = round(decimal.Decimal(euro_rate) * acc.bonus, 2)

        return context '''
        

''' # checking to see if the sender and reciever's currencies are the same or not
if giver_currency != reciever_currency:
    url = f'https://api.exchangerate.host/convert?from={giver_currency}&to={reciever_currency}'
    response = requests.get(url) # getting a response
    data = response.json() # getting the data
    ex_rate = round(decimal.Decimal(data['result']), 4)
    reciever_amount = ex_rate * MoneyToSend
    giver_currency = get_currency_symbol(giver.main_currency)
    reciever_currency = get_currency_symbol(reciever.main_currency)
else:
    reciever_amount = MoneyToSend
    ex_rate = 1
    giver_currency = get_currency_symbol(giver.main_currency)
    reciever_currency = get_currency_symbol(reciever.main_currency)'''