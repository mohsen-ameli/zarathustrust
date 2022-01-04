import decimal
import json
from django.http.response import JsonResponse
from ipware import get_client_ip
import os

import requests
from bs4 import BeautifulSoup
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

with open('/etc/config.json') as config_file:
    config = json.load(config_file)


# test function to see if the user tryna see the page is allowed to do so
def correct_user(pk):
    if pk == get_current_user().pk:
        return True
    return False


# getting the language cookie
def cookie_monster(request):
    cookies = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    if cookies is None:
        print('bruh no cookies for me', cookies)
    else:
        print('old cookies', cookies)
        translation.activate(cookies)


############# Function Based Views ############
@login_required
def HomeView(request, pk):
    if correct_user(pk):
        acc = account.objects.get(pk=request.user.pk)
        user_ = CustomUser.objects.get(pk=request.user.pk)
        url = f'https://api.exchangerate.host/convert?from=USD&to=EUR' # 1 USD to EUR
        response = requests.get(url) # getting a response
        data = response.json() # getting the data
        euro_rate = data['result']

        context = {
            'interest_list' : account_interest.objects.get(pk=request.user.pk),
            'is_bus'        : user_.is_business,
            'currency'      : user_.currency,
            'euro_rate'     : euro_rate,
            'object'        : acc
        }
        return render(request, 'accounts/home.html', context)
    else:
        raise PermissionDenied


# Admin Page
def AdminRickRoll(lmfao):
    r = redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley")
    return r


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
        project = os.path.abspath(os.path.dirname(__name__)) # root of django project
        file = f'{project}/country_languages.json' # getting the file containing all country codes
        with open(file, 'r') as config_file: # opening and reading the json file
            data = json.load(config_file)
        langs = data[country_code] # searching for our specific country code
        lang = next(iter(langs))
    translation.activate(lang)
    response = render(request, 'accounts/landing_page.html')
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
    return response


@login_required
def new_dunc(request):
    if request.user.id == 1:
        # # # celery -A money_moe worker -l info --pool=solo
        interest_loop.delay()
        return render(request, 'accounts/new_dunc.html')
    else:
        return HttpResponse("<h1>How tf did u find this page ... smh ... script kiddies these days jeez</h1>")


# Transfer Sending
@login_required
def TransferSendView(request, pk, reciever_name):
    if correct_user(pk):
        if request.method == "POST":
            form = TransferSendForm(request.POST)
            if form.is_valid():
                # Logic starts
                try:
                    reciever_pk = account.objects.get(created_by__username=reciever_name).pk # getting reciever's pk
                    purpose = form.cleaned_data.get("purpose")
                    MoneyToSend = form.cleaned_data.get("money_to_send")
                    balance = account.objects.get(pk=pk).total_balance
                    if MoneyToSend >= 1 and MoneyToSend <= balance:

                        # UPDATE ACCOUNT
                        new_total_balance = account.objects.get(pk=reciever_pk).total_balance + MoneyToSend # adding money to reciever
                        account.objects.filter(pk=reciever_pk).update(total_balance=new_total_balance)      # updating the reciever
                        a = account.objects.get(created_by=get_current_user()).total_balance # getting balance of the sender
                        rmv_total_balance = a - MoneyToSend                                  # minusing balance of sender by how much thy're sending
                        account.objects.filter(created_by=get_current_user()).update(total_balance=rmv_total_balance)      # updating the giver

                        # UPDATE ACCOUNT INTEREST
                        a = account_interest.objects.get(pk=reciever_pk).interest + MoneyToSend                  # adding money to reciever
                        account_interest.objects.filter(pk=reciever_pk).update(interest=a)                       # updating reciever
                        b = account_interest.objects.get(pk=get_current_user().pk).interest - MoneyToSend        # minusing money from giver
                        account_interest.objects.filter(pk=get_current_user().pk).update(interest=b)             # updating giver
                        
                        # success message
                        messages.success(request, _(f'${MoneyToSend} has been transfered to {reciever_name}'))

                        # emailing the reciever
                        reciever_email = CustomUser.objects.get(pk=reciever_pk).email
                        giver_username = CustomUser.objects.get(pk=get_current_user().pk).username
                        giver_email = CustomUser.objects.get(pk=get_current_user().pk).email
                        EMAIL_ID       = config.get('EMAIL_ID')
                        msg = EmailMessage(_("ZARATHUS TRUST MONEY TRANSFER"),
                                _(f"Dear {reciever_name}, <br> {giver_username} just transfered ${MoneyToSend} to your account ! <br> Purpose of Use : {purpose}"),
                                f"{EMAIL_ID}",
                                [f"{reciever_email}"]
                        )
                        msg.content_subtype = "html"
                        msg.send()

                        # emailing the giver
                        msg1 = EmailMessage(_("ZARATHUS TRUST MONEY TRANSFER"),
                                _(f"Dear {giver_username}, <br> ${MoneyToSend} has been transfered to {reciever_name} successfully ! <br> Purpose of Use : {purpose}"),
                                f"{EMAIL_ID}",
                                [f"{giver_email}"]
                        )
                        msg1.content_subtype = "html"
                        msg1.send()

                        # add the transaction to the user's history
                        person = account.objects.get(pk=get_current_user().pk)
                        second_person = account.objects.get(pk=reciever_pk)
                        r = transaction_history(person=person, second_person=second_person,
                        price=MoneyToSend, purpose_of_use=purpose, method="Transfer")
                        r.save()

                        return redirect(reverse('accounts:home', kwargs={'pk':pk}))
                    elif MoneyToSend < 1:
                        messages.warning(request, _(f'Please consider that the minimum amount to send is $1 !'))
                    elif MoneyToSend > balance:
                        messages.warning(request, _(f'You have requested to transfer more than you have in your current balance !'))
                except ObjectDoesNotExist:
                    messages.warning(request, _(f'The Account You Are Trying to Send Money to Has not Finished Signing Up !'))
            context = {"form" : form}
            return render(request, "accounts/transfer_send.html", context)
        else:
            form = TransferSendForm()
            context = {"reciever_name" : reciever_name, "form" : form}
            return render(request, "accounts/transfer_send.html", context)
    else:
        raise PermissionDenied()


# Transfer Searching
@login_required
def TransferSearchView(request, pk):
    if correct_user(pk):
        return render(request, "accounts/transfer_search.html")
        # if request.method == "POST": # target has been aquired
        #     person = request.POST.get('search_result')
        #     if person == request.user.username:
        #         messages.warning(request, _(f'Sorry, but you cannot send money to yourself'))
        #     else:
        #         print(person)
        #         return redirect(reverse("accounts:transfer-send", kwargs={"pk" : pk, "reciever_name" : person}))

        # all_acc = CustomUser.objects.values('username')
        # qs_json = json.dumps(list(all_acc), cls=DjangoJSONEncoder)
        # context = {"qs_json" : qs_json}


        # if request.method == "POST":
        #     form = TransferSearchForm(request.POST)
        #     if form.is_valid():
        #         target_account = form.cleaned_data.get('target_account')
        #         found_accounts = CustomUser.objects.all().filter(
        #             Q(email__icontains=target_account) | Q(phone_number__icontains=target_account) | Q(username__icontains=target_account)
        #         )
        #         # found_accounts = CustomUser.objects.filter(username__icontains=target_account)
        #         if not found_accounts: # no accounts were found
        #             messages.warning(request, _(f'Sorry, no account with the information provided was found :('))
        #         elif found_accounts == request.user.username:
        #             messages.warning(request, _(f'Sorry, but you cannot send money to yourself'))
        #         else: # accounts were found
        #             checkbox = request.POST.get('checkbox')
        #             if checkbox is not None: # A target user has been aquired
        #                 if str(checkbox) == str(request.user):
        #                     messages.warning(request, _(f'Sorry, but you cannot send money to yourself'))
        #                 else:
        #                     return redirect(reverse("accounts:transfer-send", kwargs={"pk" : pk, "reciever_name" : checkbox.split(',')[0]}))
        #             context = {"form" : form, "found_accounts" : found_accounts, "qs_json" : qs_json}
        #             return render(request, "accounts/transfer_search.html", context)
        # else:
        #     form = TransferSearchForm()
        # context = {"form" : form}
        # return render(request, "accounts/transfer_search.html", context)
    else:
        raise PermissionDenied()

# Transfer Searching
def search_results(request):
    if request.is_ajax():
        # getting the stuff that was typed in in transfer.html
        typed = request.POST.get('person')
        query = CustomUser.objects.all().filter(
                    Q(email__icontains=typed) | Q(phone_number__icontains=typed) | Q(username__icontains=typed)
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
            res = "No accounts were found."
        return JsonResponse({'data' : res})
    return JsonResponse({})


@login_required
def cash_out(request, pk):
    if correct_user(pk):
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
                messages.success(request, _(f'You have successfully cashed out ${round(interest_rate, 1) * 2}'))
                account_interest.objects.filter(pk=pk).update(interest_rate=0)
                account.objects.filter(pk=pk).update(bonus=bonus-round(interest_rate, 1)) # updating bonus
                r = transaction_history(person=guy, price=round(interest_rate, 1) * 2, method="Cash Out")
                r.save()
                return redirect(reverse('accounts:home', kwargs={'pk':pk}))
            else:
                total_balance = account.objects.get(pk=pk).total_balance # getting total balance
                total_balance = total_balance + bonus + interest_rate
                account.objects.filter(pk=pk).update(total_balance=total_balance) # updating total balance
                account_interest.objects.filter(pk=pk).update(interest=total_balance) # updating account interest
                messages.success(request, _(f'You have successfully cashed out ${round(interest_rate, 1) + bonus}'))
                account_interest.objects.filter(pk=pk).update(interest_rate=0)
                account.objects.filter(pk=pk).update(bonus=0) # updating bonus 
                r = transaction_history(person=guy, price=round(interest_rate, 1) + bonus, method="Cash Out")
                r.save()
                return redirect(reverse('accounts:home', kwargs={'pk':pk}))
        elif interest_rate < 0.1:
            messages.warning(request, _(f'You need at least $0.1 to be able to cash out ! keep going tho'))
            return redirect(reverse('accounts:home', kwargs={'pk':pk}))
    else:
        raise PermissionDenied()


# Referral Code
@login_required
def ReferralCodeView(request, pk):
    if correct_user(pk):
        return render(request, 'accounts/referral_code.html')
    else:
        raise PermissionDenied()


# Add Money Form
@login_required
def AddMoneyUpdateView(request, pk):
    if correct_user(pk):
        form                    = AddMoneyForm(request.POST or None)
        if form.is_valid():
            add_money           = form.cleaned_data.get('add_money')
            if add_money >= 1:
                EMAIL_ID        = config.get('EMAIL_ID')
                EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')
                send_mail(f'{get_current_user()}', 
                        f'{get_current_user()} with account number : {pk} has requested to deposit ${add_money}',
                        f'{EMAIL_ID}',
                        [f'{EMAIL_ID_MAIN}'],)
                account.objects.filter(pk=pk).update(add_money=0)
                # messages.success(request, _(f"${add_money} was requested to be put into your account"))
                return redirect(reverse('accounts:add-money-info', kwargs={'pk':pk}))
            else:
                messages.warning(request, _("Please consider that the minimum amount to withdraw must be $1 or higher !"))
                return redirect(reverse('accounts:add-money', kwargs={'pk':pk}))
        return render(request, 'accounts/add_money_form.html', {'form' : form})
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
        form                    = TakeMoneyForm(request.POST or None)
        if form.is_valid():
            take_money          = form.cleaned_data.get('take_money')
            balance             = account.objects.get(pk=pk).total_balance
            if take_money >= 1 and take_money <= balance:
                EMAIL_ID        = config.get('EMAIL_ID')
                EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')
                MOE_EMAIL       = config.get('MOE_EMAIL')
                send_mail(f'{get_current_user()}', 
                        f'{get_current_user()} with account number : {get_current_user().pk} has requested to withdraw ${take_money}',
                        f'{EMAIL_ID}',
                        [f'{EMAIL_ID_MAIN}'],)
                account.objects.filter(pk=pk).update(take_money=0)
                messages.success(request, _(f"${take_money} was requested to be taken out"))
                return redirect(reverse('accounts:home', kwargs={'pk':pk}))
            elif take_money > balance:
                messages.warning(request, _("You have requested to take more than you have in your current balance !"))
            elif take_money < 1:
                messages.warning(request, _("Please consider that the minimum amount to withdraw must be $1 or higher !"))
        return render(request, 'accounts/take_money_form.html', {'form' : form})
    else:
        raise PermissionDenied()


# About Page
def AboutTemplateView(request):
    context = {'stuff' : _('hello hello hi hi')}
    return render(request, 'accounts/about.html', context)


# DELTE this later
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
# DELTE this later
def paying_func(shop, price, buyer_balance):
    shop_owner = account.objects.get(created_by__username=shop).created_by
    shop_balance = account.objects.get(created_by=shop_owner).total_balance
    new_balance = shop_balance + price
    account.objects.filter(created_by=shop_owner).update(total_balance = new_balance)

    # subtracting the price from the buyer
    account.objects.filter(pk=get_current_user().pk).update(total_balance=buyer_balance-price)
# DELTE this later
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
        return redirect(request.META['HTTP_REFERER'])


# Checkout Page
@login_required
def checkout(request, pk, shop, price):
    if correct_user(pk):
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
    else:
        raise PermissionDenied()


pagination_number = 10
@login_required
def History(request, pk):
    if correct_user(pk):
        # combining both query sets that have the cureently logged in user's history in them
        current_logged_user    = account.objects.get(pk=pk)
        person_history         = transaction_history.objects.filter(person=current_logged_user).order_by('date').reverse()
        seconed_person_history = transaction_history.objects.filter(second_person=current_logged_user).order_by('date').reverse()
        a = person_history | seconed_person_history
        counter = Paginator(a, 1).count

        # getting the euro rate
        # url = f'https://api.exchangerate.host/convert?from=USD&to=EUR' # 1 USD to EUR
        # response = requests.get(url) # getting a response
        # data = response.json() # getting the data
        # euro_rate = round(decimal.Decimal(data['result']), 2)

        pagination_number = request.POST.get('paginate')
        if pagination_number == "all":
            pagination_number = counter
            
            
        cookies_pag = request.COOKIES.get('pag')
        print(cookies_pag)
        # paginating pages with pagination_number
        if pagination_number is not None:
            paginator = Paginator(a, pagination_number)
        else:
            if cookies_pag and cookies_pag != "None":
                paginator = Paginator(a, cookies_pag)
            else:
                paginator = Paginator(a, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        currency = CustomUser.objects.get(pk=pk).currency
        context = {"page_obj" : page_obj, "currency" : currency}

        response = render(request, "accounts/history.html", context)
        response.set_cookie('pag', pagination_number)
        return response
    else:
        raise PermissionDenied()


# History Detail Page
@login_required
def history_detail(request, pk, tran_id):
    if correct_user(pk):
        user = request.user.id
        context = transaction_history.objects.get(pk=tran_id)
        if context.person.id == user or context.second_person.id == user :
            return render(request, "accounts/history_detail.html", {"context" : context})
        else: 
            raise PermissionDenied()
    else:
        raise PermissionDenied()





# Class Based Views
# class HomeView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
#     model = account
#     template_name = 'accounts/home.html'

#     def test_func(self):
#         account = self.get_object()
#         if self.request.user == account.created_by:
#             return True
#         return False

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['interest_list'] = account_interest.objects.get(pk=get_current_user().pk)
#         context['is_bus'] = CustomUser.objects.get(pk=get_current_user().pk).is_business
#         context['currency'] = CustomUser.objects.get(pk=get_current_user().pk).currency

#         acc = account.objects.get(pk=get_current_user().pk)

#         url = f'https://api.exchangerate.host/convert?from=USD&to=EUR' # 1 USD to EUR
#         response = requests.get(url) # getting a response
#         data = response.json() # getting the data
#         euro_rate = data['result'] # extracting the desired column and converting it into Decimal django field
#         context['euro_balance'] = round(decimal.Decimal(euro_rate) * acc.total_balance, 2) # set the EUR balance to euro_balance for templates
#         context['euro_rate']    = euro_rate  # passing euro_rate for 1 USD
#         context['euro_bonus']   = round(decimal.Decimal(euro_rate) * acc.bonus, 2)

#         return context