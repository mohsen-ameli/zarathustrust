import json
import os
import phonenumbers
from ipware import get_client_ip
import requests

from accounts.models import account
from crum import get_current_user
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.conf import settings

from .forms import (BusinessForm, EmailCodeForm, PhoneCodeForm,
                    ReferralCodeForm, RegisterForm)
from .models import CustomUser, code
from .utils import phone_msg_verify

with open("/etc/config.json") as config_file:
    config = json.load(config_file)


def country_from_ip(request):
    # getting the visitors country, ip address
    ip, is_routable = get_client_ip(request)
    if ip is None:
        # Unable to get the client's IP address
        name = None
        code = None
        return name, code
    else:
        # We got the client's IP address
        if is_routable:
            # The client's IP address is publicly routable on the Internet
            url = f"https://geolocation-db.com/json/{ip}&position=true"
            response = requests.get(url).json()
            # print(response)
            name = response['country_name']
            code = response['country_code']
            return name, code
        else:
            # The client's IP address is private
            name = None
            code = None
            return name, code


# setting cookies 
# def cookie_monster(request):
    # cookies = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    # if cookies is None: # no cookies
    #     print('NEW cookies', cookies)
    #     if request.user.is_authenticated == True:
    #         lang = CustomUser.object.get(pk=request.user.pk).language
    #         translation.activate(lang)
    #     else:
    #         ip, is_routable = get_client_ip(request)
    #         if ip is None:
    #             code = None
    #         else:
    #             if is_routable:
    #                 url = f"https://geolocation-db.com/json/{ip}&position=true"
    #                 response = requests.get(url).json()
    #                 code = response['country_code']
    #             else:
    #                 code = None
    #         EN = ['Canada', 'canada', 'CA', 'ca', 'USA', 'US', 'United States', 'United States of America', 'Australias', 'UK', 'England', 'United Kingdom', 'Jamaica']
    #         if code in EN:
    #             code = 'en'
    #         translation.activate(code)
    # else: # cookies exist already
    #     print("OLD cookies", cookies)
    #     translation.activate(cookies)


# getting country languages
def get_country_lang(country_code):
    country_code = country_code.upper()
    project = os.path.abspath(os.path.dirname(__name__)) # root of django project
    file = f'{project}/country_languages.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)
    langs = data[country_code] # searching for our specific country code
    lang = next(iter(langs))
    return lang


# getting country currency
def get_country_currency(country_code):
    country_code = country_code.upper()
    project = os.path.abspath(os.path.dirname(__name__)) # root of django project
    file = f'{project}/country_currencies.json' # getting the file containing all country codes
    with open(file, 'r') as config_file: # opening and reading the json file
        data = json.load(config_file)

    return data[country_code]


def register(request):
    if request.user.is_anonymous == True:
        country = country_from_ip(request)[1]
        if country is None:
            lang = 'en'
        else:
            lang = get_country_lang(country)
        response = render(request, "users/register.html")
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
    else:
        return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))


def business(request):
    if request.user.is_anonymous == True:
        if request.method == "POST":
            form = BusinessForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password1")
                user_ = authenticate(request, username=username, password=password)
                if user_ is not None:
                    request.session["pk"] = user.pk
                    messages.success(request, _(f"HIIIII"))

                    country = country_from_ip(request)[1]
                    if country is None:
                        country = 'en'
                    else:
                        lang = get_country_lang(country)
                    response = redirect("/")
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
                    return response
                else:
                    # Return an 'invalid login' error message.
                    country = country_from_ip(request)[1]
                    if country is None:
                        country = 'en'
                    else:
                        lang = get_country_lang(country)
                    response = redirect("/")
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
                    return response
        else:
            form = BusinessForm()
        country = country_from_ip(request)[1]
        if country is None:
            lang = 'en'
        else:
            lang = get_country_lang(country)
        response = render(request, "users/business.html", {"form": form})
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
    else:
        return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))


def PersonalCountryPickSignUp(request):
    if request.user.is_anonymous == True:
        default_country = country_from_ip(request)
        if request.method == "POST":
            country_code = request.POST.get('country-picker')
            if country_code:
                response = redirect(reverse("personal-sign-up", kwargs={"country" : country_code}))
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, country_code)
                return response
            else:
                context = {"default_country" : default_country[0], "default_country_code" : default_country[1]}
                response = render(request, "users/country_pick.html", context)
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, country_code)
                return response
        else:
            context = {"default_country" : default_country[0], "default_country_code" : default_country[1]}
            country = country_from_ip(request)[1]
            if country is None:
                lang = 'en'
            else:
                lang = get_country_lang(country)
            response = render(request, "users/country_pick.html", context)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
            return response
    else:
        return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))


def PersonalSignUp(request, country):
    if request.user.is_anonymous == True:
        ext = phonenumbers.country_code_for_region(country)
        if request.method == "POST":
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password1")
                user_ = authenticate(request, username=username, password=password)

                # getting countries currency
                currency = get_country_currency(country)

                # getting countries language
                lang = get_country_lang(country)
                
                # updating the user object to include the currency, language, and country
                CustomUser.objects.filter(username=username).update(country=country, currency=currency, phone_ext=ext, language=lang)
                if user_ is not None:
                    request.session["pk"] = user.pk
                    messages.success(
                        request,
                        _(
                            f"Please check your mailbox (as well as spam folder) for a verification code, and enter the 5-digit code below"
                        ),
                    )
                    return redirect("verify-view")
                else:
                    # Return an 'invalid login' error message.
                    return redirect("/")
        else:
            form = RegisterForm()
        return render(request, "users/personal.html", {"form": form, "ext" : ext})
    else:
        return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))


def email_verify_view(request):
    if request.user.is_anonymous == True:
        form = EmailCodeForm(request.POST or None)
        pk = request.session.get("pk")
        if pk:
            user = CustomUser.objects.get(pk=pk)
            email_code = user.code.email_verify_code
            if not request.POST:
                # send email
                EMAIL_ID = config.get("EMAIL_ID")
                send_mail(
                    _(f"Hello {user.username}"),
                    _(
                        f"Your verification code is : {email_code}, you are very close to starting your money making process!"
                    ),
                    f"{EMAIL_ID}",
                    [f"{user.email}"],
                )
            if form.is_valid():
                num = form.cleaned_data.get("email_verify_code")
                if str(email_code) == num:
                    messages.success(
                        request,
                        _(
                            f"Please check your phone for verification code, and enter the 5-digit code below"
                        ),
                    )
                    return redirect("phone-verify-view")
                else:
                    messages.warning(
                        request,
                        _(f"You enterd the wrong verificaiton code ! Please try again"),
                    )
        return render(request, "users/email_verify.html", {"form": form})
    else:
        return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))


def phone_verify_view(request):
    if request.user.is_anonymous == True:
        form = PhoneCodeForm(request.POST or None)
        pk = request.session.get("pk")
        if pk:
            user = CustomUser.objects.get(pk=pk)
            phone_code = user.code.phone_verify_code
            phone_number = user.phone_number
            if not request.POST:
                # send SMS
                phone_msg_verify(
                    verify_code=phone_code, phone_number_to=phone_number
                )
            if form.is_valid():
                num = form.cleaned_data.get("phone_verify_code")
                if str(phone_code) == num:
                    if CustomUser.objects.get(pk=pk).iban != "":
                        messages.success(
                            request,
                            _(
                                f"Enter your friend's referral code in order for both of you to get grand prize !"
                            ),
                        )
                        return redirect("referral-verify-view")
                    else:
                        messages.success(
                            request,
                            _(
                                f"Enter your friend's referral code in order for both of you to get grand prize !"
                            ),
                        )
                        return redirect("referral-verify-view")
                else:
                    messages.warning(
                        request,
                        _(f"You enterd the wrong verificaiton code ! Please try again"),
                    )
        return render(request, "users/phone_verify.html", {"form": form})
    else:
        return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))


def referral_verify_view(request, backend='django.contrib.auth.backends.ModelBackend'):
    if request.user.is_anonymous == True:
        form = ReferralCodeForm(request.POST or None)
        pk = request.session.get("pk")
        if pk:
            user = CustomUser.objects.get(pk=pk)
            if form.is_valid():
                enterd_code = form.cleaned_data.get("referral_code")
                friend_code = code.objects.all().filter(referral_code=enterd_code)
                if friend_code:  # referral code exists
                    user.code.save()
                    login(request, user, backend)

                    account.objects.create(created_by=user, bonus=1200, pk=user.pk)
                    giver_name = code.objects.get(referral_code=enterd_code).user
                    new_bal = account.objects.get(created_by=giver_name).total_balance
                    ref = account.objects.get(created_by=giver_name).bonus
                    account.objects.filter(created_by=giver_name).update(
                        total_balance=new_bal + 1
                    )
                    account.objects.filter(created_by=giver_name).update(bonus=ref + 200)
                    # send email
                    EMAIL_ID = config.get("EMAIL_ID")
                    GIVER_EMAIL = CustomUser.objects.get(pk=user.pk).email
                    send_mail(
                        _(f"Dear {giver_name} !"),
                        _(
                            f"{user.username} just used your referral code ! You recieved $1 on your balance, and $200 added to your bonus !"
                        ),
                        f"{EMAIL_ID}",
                        [f"{GIVER_EMAIL}"],
                    )
                    messages.success(
                        request,
                        _(
                            f"You have successfully registered, {user.username}. For your prize, $200 will be transfered to your bonus !"
                        ),
                    )
                    return redirect(
                        reverse("accounts:home", kwargs={"pk": user.account.pk})
                    )
                elif enterd_code == "":  # referral code not submitted
                    user.code.save()
                    login(request, user, backend)
                    account.objects.create(created_by=user, pk=user.pk)
                    messages.success(
                        request, _(f"You have successfully registered, {user.username} !")
                    )
                    return redirect(
                        reverse("accounts:home", kwargs={"pk": user.account.pk})
                    )
                else:  # referral code incorrect
                    user.code.save()
                    login(request, user, backend)
                    account.objects.create(created_by=user, pk=user.pk)
                    messages.success(
                        request,
                        _(
                            f"Sorry, this referral code is incorrect, but you have successfully registered, {user.username} !"
                        ),
                    )
                    return redirect(
                        reverse("accounts:home", kwargs={"pk": user.account.pk})
                    )
        return render(request, "users/referral_code.html", {"form": form})
    else:
        return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))


def auth_view(request, url1, url2, url3, url4):
    if request.user.is_anonymous == True:
        form = AuthenticationForm()
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(
                    reverse(
                        "accounts:payment",
                        kwargs={"url1": url1, "url2": url2, "url3": url3, "url4": url4},
                    )
                )
        return render(request, "users/login.html", {"form": form})
    else:
        return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))


def LoginClassView(request):
    if request.user.is_anonymous == True:
        form = AuthenticationForm()
        template_name = "users/login.html"
        next = request.GET.get('next')
        if request.method == 'POST' and next is None:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page.
                user_language = CustomUser.objects.get(pk=request.user.pk).language
                response = redirect(reverse("accounts:home", kwargs={"pk" : request.user.pk}))
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
                return response
            else:
                messages.warning(request, _("Please enter a correct username and password. Note that both fields are case-sensitive."))
        elif request.method == 'POST' and next is not None:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page.
                user_language = CustomUser.objects.get(pk=request.user.pk).language
                response = redirect(next)
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
                return response
        return render(request, template_name, {'form' : form})
    else:
        return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))


# class LoginClassView(LoginView):
    # template_name = "users/login.html"

    # I commented this out, becuase I want users to be able to be redirected to their specific
    # pages after they log in. eg: say someone comes from a shop to /checkout then they have to 
    # first login, then be immidietly redirected to that checkout page, by using the login_required 
    # decorator, but if i have this get_success_url then it will overwrite the ?next parameter and
    # mess up the proccess.

    # def get_success_url(self):
    #     # url = self.get_redirect_url()
    #     return reverse_lazy(
    #         "accounts:home", kwargs={"pk": get_current_user().account.pk}
    #     )


# def iban_verify_view(request):
#     if request.user.is_anonymous == True:
#         form = IbanCodeForm(request.POST or None)
#         pk = request.session.get("pk")
#         if pk:
#             user = CustomUser.objects.get(pk=pk)
#             iban_code = user.code.iban_verify_code
#             if not request.POST:
#                 # send email
#                 # iban_number = CustomUser.objects.get(pk=pk).iban
#                 EMAIL_ID = config.get("EMAIL_ID")
#                 MOE_EMAIL = config.get("MOE_EMAIL")
#                 send_mail(
#                     f"IBAN verficication code for {user.username}",
#                     f"The IBAN verification code for user : {user.username} is : {iban_code}",
#                     f"{EMAIL_ID}",
#                     [f"{MOE_EMAIL}"],
#                 )
#             if form.is_valid():
#                 num = form.cleaned_data.get("iban_verify_code")
#                 if str(iban_code) == num:
#                     messages.success(
#                         request,
#                         _(
#                             f"Enter your friend's referral code in order for both of you to get grand prize !"
#                         ),
#                     )
#                     return redirect("referral-verify-view")
#         return render(request, "users/iban_verify.html", {"form": form})
#     else:
#         return redirect(reverse("accounts:home", kwargs={'pk' : request.user.pk}))
# messages.success(
#     request,
#     _(
#         f"Please wait for our support team to send you a pre-decided amount of money. Check your bank account and then enter the small amount bellow."
#     ),
# )
# return redirect("iban-verify-view")