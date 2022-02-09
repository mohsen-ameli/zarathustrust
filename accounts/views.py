import os
import decimal
import json
import requests

from django.http.response import JsonResponse
from ipware import get_client_ip
from crum import get_current_user

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.core.exceptions import PermissionDenied
from django.db.models import Q
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
from .functions import currency_symbol, currency_min, correct_user
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
    if correct_user(pk):
        acc         = account.objects.get(pk=pk) # user's account
        user_       = CustomUser.objects.get(pk=pk) # user's model
        currency    = currency_symbol(user_.currency) # user model's currency
        branch_acc  = BranchAccounts.objects.filter(main_account__pk=pk) # getting user's wallets

        # loading the country currencies clean json file
        project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file = f'{project}/json/country_currencies_clean.json'
        with open(file, 'r') as config_file:
            data = json.load(config_file)

        # if user selected a country
        wallet_name = request.GET.get("wallet-name")
        if wallet_name:
            wallet_name = wallet_name.upper()
            # testing to see if the entered GET arg actually exists in the user's wallet currency column
            test = branch_acc.filter(currency=wallet_name).exists()
            if test is not False or user_.currency == wallet_name:

                # list = (country_iso2, currency, symbol, balance)
                wallets = []

                # putting the first element of the list as the user's main currency
                if acc.main_currency != wallet_name:
                    for a in data:
                        if data[a] == acc.main_currency:
                            wallets.append((a, acc.main_currency, currency, acc.total_balance))

                # attaching every wallet to our list
                for item in branch_acc.exclude(currency=wallet_name):
                    for i in data:
                        if data[i] == item.currency:
                            wallets.append((i, item.currency, currency_symbol(item.currency), item.total_balance))

                # setting variables for our context
                for i in data:
                    if data[i] == wallet_name:
                        wallet_iso       = i
                        wallet_currency  = data[i]
                        wallet_symbol    = currency_symbol(data[i])
                        try:
                            wallet_balance   = branch_acc.get(currency=data[i]).total_balance
                        except:
                            wallet_balance = acc.total_balance
            else:
                wallet_name = None
        
        # default view of the user's account
        if wallet_name is None:
            # show users their default wallet
            for i in data:
                if data[i] == acc.main_currency:
                    wallet_iso       = i
                    wallet_currency  = data[i]
                    wallet_symbol    = currency_symbol(data[i])
                    wallet_balance   = acc.total_balance

            wallets = []
            for wallet in branch_acc:
                for a in data:
                    if data[a] == wallet.currency:
                        wallets.append((a ,wallet.currency, currency_symbol(wallet.currency)))

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
    else:
        raise PermissionDenied


# Settings
@login_required
def Settings(request, pk):
    context = {
        "pk" : pk
    }
    return render(request, "accounts/settings.html", context)


# Settings Country search
@login_required
def SettingsCountry(request, pk):
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
    if correct_user(pk):
        # getting user's currency stuff
        User                = CustomUser.objects.get(pk=request.user.pk)
        currency_name       = User.currency
        currency_symbol_    = currency_symbol(currency_name)
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
                currency_symbol_    = currency_symbol(currency_GET)
                currency_name       = currency_GET
                min_currency        = currency_min(currency_name)
                balance             = giver_wallet.get(currency=currency_GET).total_balance
        
        branch_acc = BranchAccounts.objects.filter(main_account__pk=pk)
        for wallet in branch_acc:
            currency_options.append((wallet.currency, currency_symbol(wallet.currency)))
        
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
                            # reciever and giver's accounts do not have the same currency
                            if giver_currency == currency_name:
                                # account-to-somthing
                                giver_total_balance = balance
                                giver_update = account.objects.filter(pk=pk)
                                if reciever_wallet.filter(currency=currency_name).exists():
                                    # account-to-wallet
                                    print("account-to-wallet")
                                    reciever_total_balance = reciever_wallet.filter(currency=currency_name).values("total_balance")[0]['total_balance']
                                    reciever_update = reciever_wallet.filter(currency=currency_name)
                                    update_interest_rate = False
                                elif giver_currency == reciever_currency and currency_name:
                                    # account-to-account
                                    print("account-to-account")
                                    reciever_total_balance = reciever.total_balance
                                    reciever_update = account.objects.filter(created_by__username=reciever_name)
                                    update_interest_rate = True
                                else:
                                    # account-to-newWallet
                                    print("account-to-newWallet")
                                    # creating a new wallet for reciever
                                    BranchAccounts.objects.create(main_account=reciever, currency=giver_currency)
                                    reciever_total_balance = 0
                                    reciever_update = BranchAccounts.objects.filter(main_account=reciever)
                                    update_interest_rate = False
                            else:
                                # wallet-to-something
                                giver_total_balance = giver_wallet.filter(currency=currency_name).values("total_balance")[0]['total_balance']
                                giver_update = giver_wallet.filter(currency=currency_name)
                                giver_wallet.filter(currency=currency_name)
                                if reciever_wallet.filter(currency=currency_name).exists():
                                    # wallet-to-wallet
                                    print("wallet-to-wallet")
                                    reciever_total_balance = reciever_wallet.filter(currency=currency_name).values("total_balance")[0]['total_balance']
                                    reciever_update = reciever_wallet.filter(currency=currency_name)
                                    update_interest_rate = False
                                elif reciever.main_currency == currency_name:
                                    # wallet-to-account
                                    print("wallet-to-account")
                                    reciever_total_balance = reciever.total_balance
                                    reciever_update = account.objects.filter(created_by__username=reciever_name)
                                    update_interest_rate = True
                                else:
                                    # wallet-to-newWallet
                                    print("wallet-to-newWallet")
                                    # creating a new wallet for reciever
                                    BranchAccounts.objects.create(main_account=reciever, currency=currency_name)
                                    reciever_total_balance = 0
                                    reciever_update = BranchAccounts.objects.filter(main_account=reciever)
                                    update_interest_rate = False
                            
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
                                # adding money to reciever
                                a = reciever_interest.interest + MoneyToSend
                                # updating reciever
                                account_interest.objects.filter(pk=reciever.pk).update(interest=a)
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
                            # r = transaction_history(person=giver, second_person=reciever,
                            # price=MoneyToSend, ex_rate=ex_rate, ex_price=reciever_amount, purpose_of_use=purpose, method="Transfer")
                            # r.save()

                            return redirect(reverse('accounts:home', kwargs={'pk':pk}))
                        elif MoneyToSend < min_currency:
                            messages.warning(request, _(f'Please consider that the minimum amount to send is {currency_symbol_}{min_currency} !'))
                        elif MoneyToSend > balance:
                            messages.warning(request, _(f'You have requested to transfer more than you have in your current balance !'))
                    else:
                        messages.warning(request, _(f'You cannot send money to yourself.'))
                except ObjectDoesNotExist:
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
    else:
        raise PermissionDenied()


# Money Send Searching
@login_required
def TransferSearchView(request, pk):
    if correct_user(pk):
        return render(request, "accounts/transfer_search.html")
    else:
        raise PermissionDenied()


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
def cash_out(request, pk):
    if correct_user(pk):
        # getting user's currency stuff
        user_ = CustomUser.objects.get(pk=request.user.pk)
        currency = currency_symbol(user_.currency)
        
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
    else:
        raise PermissionDenied()


# Referral Code
@login_required
def ReferralCodeView(request, pk):
    if correct_user(pk):
        a = ReferralCode.objects.get(user=request.user).referral_code
        return render(request, 'accounts/referral_code.html', {"referral_code" : a})
    else:
        raise PermissionDenied()


# Add Money Form
@login_required
def AddMoneyUpdateView(request, pk):
    if correct_user(pk):
        # getting user's currency stuff
        user_               = CustomUser.objects.get(pk=request.user.pk)
        currency_name       = user_.currency
        currency_symbol_    = currency_symbol(currency_name)
        min_currency        = currency_min(currency_name)
        currency_options    = [(currency_name, currency_symbol_)] # currencies that will be showed as options

        if request.GET.get("currency"):
            currency_GET        = request.GET.get("currency").upper()
            # testing to see if the entered GET arg actually exists in the user's wallet currency column
            test = BranchAccounts.objects.filter(main_account__pk=pk).filter(currency=currency_GET).exists()
            if test is not False:
                currency_symbol_    = currency_symbol(currency_GET)
                currency_name       = currency_GET
                min_currency        = currency_min(currency_name)

        branch_acc = BranchAccounts.objects.filter(main_account__pk=pk)
        for wallet in branch_acc:
            currency_options.append((wallet.currency, currency_symbol(wallet.currency)))


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
    else:
        raise PermissionDenied()


# Add Money Info
@login_required
def AddMoneyInfo(request, pk):
    if correct_user(pk):
        return render(request, 'accounts/add_money_info.html')
    else:
        raise PermissionDenied()


# Take Money Form
@login_required
def TakeMoneyUpdateView(request, pk):
    if correct_user(pk):
        # getting user's currency stuff
        user_               = CustomUser.objects.get(pk=request.user.pk)
        currency_name       = user_.currency
        currency_symbol_    = currency_symbol(currency_name)
        min_currency        = currency_min(currency_name)
        balance             = account.objects.get(pk=pk).total_balance
        branch_acc          = BranchAccounts.objects.filter(main_account__pk=pk)

        # currencies that will be showed as options
        currency_options    = [(currency_name, currency_symbol_)]

        if request.GET.get("currency"):
            currency_GET        = request.GET.get("currency").upper()
            # testing to see if the entered GET arg actually exists in the user's wallet currency column
            test = BranchAccounts.objects.filter(main_account__pk=pk).filter(currency=currency_GET).exists()
            if test is not False:
                currency_symbol_    = currency_symbol(currency_GET)
                currency_name       = currency_GET
                min_currency        = currency_min(currency_name)
                balance             = branch_acc.get(currency=currency_GET).total_balance

        for wallet in branch_acc:
            currency_options.append((wallet.currency, currency_symbol(wallet.currency)))

        form                    = TakeMoneyForm(request.POST or None)
        if form.is_valid():
            take_money          = form.cleaned_data.get('take_money')
            if take_money >= min_currency and take_money <= balance:
                EMAIL_ID        = config.get('EMAIL_ID')
                EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')
                MOE_EMAIL       = config.get('MOE_EMAIL')
                send_mail(f'{get_current_user()}', 
                        f'{get_current_user()} with account number : {get_current_user().pk} has requested to withdraw {currency_symbol_}{take_money}',
                        f'{EMAIL_ID}',
                        [f'{EMAIL_ID_MAIN}'],)
                account.objects.filter(pk=pk).update(take_money=0)
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
    else:
        raise PermissionDenied()


# Checkout Page
@login_required
def checkout(request, shop, price):
    pk = request.user.pk
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
    if correct_user(pk):
        # getting user's currency stuff
        currency               = account.objects.get(pk=pk).main_currency
        user_currency_symbol   = currency_symbol(currency)

        # combining both query sets that have the cureently logged in user's history in them
        current_logged_user    = account.objects.get(pk=pk)
        person_history         = transaction_history.objects.filter(person=current_logged_user).order_by('date').reverse()
        seconed_person_history = transaction_history.objects.filter(second_person=current_logged_user).order_by('date').reverse()
        a = person_history | seconed_person_history
        counter = Paginator(a, 1).count

        if request.GET.get("num"):
            pagination_number = request.GET.get('num') or 10
            if request.GET.get('num') == "all":
                pagination_number = counter
            paginator   = Paginator(a, pagination_number)
            page_number = request.GET.get('page')
            page_obj    = paginator.get_page(page_number)

            context = {
                "page_obj"             : page_obj,
                "currency"             : currency,
                "pagination_number"    : pagination_number,
                "counter"              : counter,
                "user_currency_symbol" : user_currency_symbol
            }
            return render(request, "accounts/history.html", context)
        else:
            paginator   = Paginator(a, 10)
            page_number = request.GET.get('page')
            page_obj    = paginator.get_page(page_number)

            context = {
                "page_obj"             : page_obj, 
                "currency"             : currency, 
                "pagination_number"    : 10, 
                "counter"              : counter,
                "user_currency_symbol" : user_currency_symbol
            }
            return render(request, "accounts/history.html", context)
    else:
        raise PermissionDenied()


# History Detail Page
@login_required
def history_detail(request, pk, tran_id):
    if correct_user(pk):
        user = request.user.id
        object = transaction_history.objects.get(pk=tran_id)
        my_currency = account.objects.get(pk=pk).main_currency
        user_currency_symbol   = currency_symbol(my_currency)
        incoming_currency = account.objects.get(pk=object.person.pk).main_currency
        incoming_currency_symbol = currency_symbol(incoming_currency)
        # incoming_currency = currency_symbol(object.person.main_currency)
        
        context = {
            "object" : object,
            "user_currency_symbol" : user_currency_symbol,
            "my_currency" : my_currency,
            "incoming_currency" : incoming_currency,
            "incoming_currency_symbol" : incoming_currency_symbol
        }
        if object.person.id == user or object.second_person.id == user :
            return render(request, "accounts/history_detail.html", context)
        else: 
            raise PermissionDenied()
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
    giver_currency = currency_symbol(giver.main_currency)
    reciever_currency = currency_symbol(reciever.main_currency)
else:
    reciever_amount = MoneyToSend
    ex_rate = 1
    giver_currency = currency_symbol(giver.main_currency)
    reciever_currency = currency_symbol(reciever.main_currency)'''