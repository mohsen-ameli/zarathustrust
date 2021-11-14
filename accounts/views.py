import decimal
import json
from os import error

import requests
from bs4 import BeautifulSoup
from crum import get_current_user
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models.base import ObjectDoesNotExist
from django.shortcuts import redirect, render
# from django.contrib.messages.views import SuccessMessageMixin
from django.urls.base import reverse
from django.utils.translation import gettext as _
from django.views.generic import DetailView, TemplateView
from requests.api import get
from users.models import CustomUser
from django.http import HttpResponse


from .forms import AddMoneyForm, TakeMoneyForm, TransferForm
from .models import account, account_interest
from .tasks import interest_loop

with open('/etc/config.json') as config_file:
    config = json.load(config_file)


# Class Based Views
class HomeTemplateView(TemplateView):
    template_name = 'accounts/home_new.html'


class HomeView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = account
    template_name = 'accounts/home.html'

    def test_func(self):
        account = self.get_object()
        if self.request.user == account.created_by:
            return True
        return False

    def get_context_data(self, **kwargs):
        pk = account.objects.get(created_by=get_current_user()).pk
        context = super().get_context_data(**kwargs)
        context['interest_list'] = account_interest.objects.get(pk=pk)
        id = CustomUser.objects.get(pk=get_current_user().pk).pk
        context['is_bus'] = CustomUser.objects.get(pk=id).is_business
        return context


# Function Based Views
def AdminRickRoll(TemplateView):
    r = redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley")
    return r


@login_required
def new_dunc(request):
    # # # celery -A money_moe worker -l info --pool=solo
    interest_loop.delay()
    return render(request, 'accounts/new_dunc.html')


@login_required
def TransferCreateView(request, pk):
    if request.method == "POST":
        form = TransferForm(request.POST)
        if form.is_valid():
            target_account = form.cleaned_data.get('target_account')
            MoneyToSend    = form.cleaned_data.get('money_to_send')

            found_accounts = CustomUser.objects.all().filter(
                Q(email__icontains=target_account) | Q(phone_number__contains=target_account) | Q(username__icontains=target_account)
            )
            if not found_accounts:
                messages.warning(request, _(f'Sorry, no account with the information provided was found :('))
            checkbox = request.POST.get('checkbox')

            if checkbox is not None: # A target user has been aquired
                target_acc = account.objects.get(created_by__username=checkbox).created_by
                reciever_pk = account.objects.get(created_by__username=checkbox).pk # getting reciever's pk
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
                    
                    messages.success(request, _(f'${MoneyToSend} has been transfered to {target_acc}'))
                    return redirect(reverse('accounts:home', kwargs={'pk':pk}))
                elif MoneyToSend < 1:
                    messages.warning(request, _(f'Please consider that the minimum amount to send is $1 !'))
                elif MoneyToSend > balance:
                    messages.warning(request, _(f'You have requested to transfer more than you have in your current balance !'))

            context = {'form' : form, 'found_accounts' : found_accounts, 'pk' : pk}
            return render(request, 'accounts/transfer.html', context)
    else:
        form = TransferForm()
    return render(request, 'accounts/transfer.html', {'form' : form})


@login_required
def cash_out(request, pk):
    interest_rate     = account_interest.objects.get(pk=pk).interest_rate
    bonus             = account.objects.get(pk=pk).bonus
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
            return redirect(reverse('accounts:home', kwargs={'pk':pk}))
        else:
            total_balance = account.objects.get(pk=pk).total_balance # getting total balance
            total_balance = total_balance + bonus + interest_rate
            account.objects.filter(pk=pk).update(total_balance=total_balance) # updating total balance
            account_interest.objects.filter(pk=pk).update(interest=total_balance) # updating account interest
            messages.success(request, _(f'You have successfully cashed out ${round(interest_rate, 1) + bonus}'))
            account_interest.objects.filter(pk=pk).update(interest_rate=0)
            account.objects.filter(pk=pk).update(bonus=0) # updating bonus 
            return redirect(reverse('accounts:home', kwargs={'pk':pk}))
    elif interest_rate < 0.1:
        messages.warning(request, _(f'You need at least $0.1 to be able to cash out ! keep going tho'))
        return redirect(reverse('accounts:home', kwargs={'pk':pk}))


@login_required
def ReferralCodeView(request, pk):
    return render(request, 'accounts/referral_code.html')


@login_required
def AddMoneyUpdateView(request, pk):
    form                    = AddMoneyForm(request.POST or None)
    if form.is_valid():
        add_money           = form.cleaned_data.get('add_money')
        if add_money >= 1:
            EMAIL_ID        = config.get('EMAIL_ID')
            EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')
            MOE_EMAIL       = config.get('MOE_EMAIL')
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


@login_required
def AddMoneyInfo(request, pk):
    return render(request, 'accounts/add_money_info.html')


@login_required
def TakeMoneyUpdateView(request, pk):
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
                    [f'{EMAIL_ID_MAIN}', f'{MOE_EMAIL}'],)
            account.objects.filter(pk=pk).update(take_money=0)
            messages.success(request, _(f"${take_money} was requested to be taken out"))
            return redirect(reverse('accounts:home', kwargs={'pk':pk}))
        elif take_money > balance:
            messages.warning(request, _("You have requested to take more than you have in your current balance !"))
            return redirect(reverse('accounts:take-money', kwargs={'pk':pk}))
        elif take_money < 1:
            messages.warning(request, _("Please consider that the minimum amount to withdraw must be $1 or higher !"))
            return redirect(reverse('accounts:take-money', kwargs={'pk':pk}))
    return render(request, 'accounts/take_money_form.html', {'form' : form})


def AboutTemplateView(request):
    context = {
        'stuff' : _('hello hello hi hi'),
    }
    return render(request, 'accounts/about.html', context)


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


def paying_func(shop, price, buyer_balance):
    shop_owner = account.objects.get(created_by__username=shop).created_by
    shop_balance = account.objects.get(created_by=shop_owner).total_balance
    new_balance = shop_balance + price
    account.objects.filter(created_by=shop_owner).update(total_balance = new_balance)

    # subtracting the price from the buyer
    account.objects.filter(pk=get_current_user().pk).update(total_balance=buyer_balance-price)


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


@login_required
def checkout(request, shop, price):
    if "$" in price:
        price = price.replace("$", '')
    total_balance = account.objects.get(created_by=request.user).total_balance
    remaining     = round(total_balance - decimal.Decimal(float(price)), 2)
    context = {'price' : price, 'balance' : total_balance, 'remaining' : remaining, 'shop' : shop}
    return render(request, "accounts/checkout.html", context)


@login_required
def checkout_complete(request, shop, price):
    while "," in price:
        translation_table = dict.fromkeys(map(ord, ','), None)
        price = price.translate(translation_table)
    price = decimal.Decimal(float(price)) # compatibilizing str price to decimalField in models 

    # Checking to see if the buyer has enough money
    buyer_balance = account.objects.get(pk=get_current_user().pk).total_balance
    if buyer_balance >= round(price, 2):
        shop_balance = account.objects.get(created_by__username=shop).total_balance
        # adding price to the shop owner
        account.objects.filter(created_by__username=shop).update(total_balance=shop_balance + price)
        # subtracting price from buyer
        account.objects.filter(pk=get_current_user().pk).update(total_balance=buyer_balance-price)

        messages.success(request, _("Your order was purchased successfully !"))
        return HttpResponse('<script type="text/javascript">window.close();</script>')
        # return redirect(reverse("accounts:home", kwargs={"pk" : get_current_user().pk}))
    else:
        messages.warning(request, _("You do not have enough money for this order !"))
        return redirect(reverse("accounts:add-money", kwargs={"pk" : get_current_user().pk}))








# class TransferTakeUpdateView(SuccessMessageMixin, UpdateView):
#     model = account
#     fields = ['take_money']
#     template_name = 'accounts/take_money_form.html'
#     success_message = _("$%(take_money)s was request to be taken out")

# @login_required
# def TransferCreateView(request, pk):
#     form    = TransferForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#         messages.success(request, _(f'${form.money_to_send} was transfered successfully'))
#         return reverse(redirect('account:home', kwargs={'pk':get_current_user().pk}))

# class TransferCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
#     model = transfer
#     form_class = TransferForm
#     success_message = _("$%(money_to_send)s was transfered successfully")
