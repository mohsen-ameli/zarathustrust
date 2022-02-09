import json
import os
import phonenumbers

from accounts.models import account
from crum import get_current_user
from django.http.response import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.conf import settings


from .forms import (BusinessForm, EmailCodeForm, PhoneCodeForm,
                    ReferralCodeForm, RegisterForm)
from .models import CustomUser, code, ReferralCode
from .utils import phone_msg_verify
from .functions import country_from_ip, get_country_lang, get_country_currency
from accounts.views import currency_min, currency_symbol

with open("/etc/config.json") as config_file:
    config = json.load(config_file)


################ Views ###############

# Initial Register Page
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
        return redirect("accounts:home", pk=request.user.pk)


# Business Register
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
        return redirect("accounts:home", pk=request.user.pk)


# view to handle the country picking
def PersonalCountryPickSignUp(request):
    if request.user.is_anonymous == True:
        default_country = country_from_ip(request)

        project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file = f'{project}/json/country_names.json' # getting the file containing all country codes
        with open(file, 'r') as config_file: # opening and reading the json file
            data = json.load(config_file)

        all_countries = data.items()

        if request.method == "POST":
            default_country_picker = request.POST.get('default-country-picker')
            if default_country_picker != None: 
                response = redirect("users:personal-sign-up", country = default_country)
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, default_country[1])
                return response
            country_code = request.POST.get('country-picker')
            if country_code:
                country_code = country_code.upper()
                response = redirect("users:personal-sign-up", country = country_code)
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, country_code)
                return response
            context = {
                "default_country" : default_country[0], 
                "default_country_code" : default_country[1], 
                "countries" : all_countries,
                "data" : data
            }
            response = render(request, "users/country_pick.html", context)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, country_code)
            return response
        else:
            context = {
                "default_country" : default_country[0], 
                "default_country_code" : default_country[1], 
                "countries" : all_countries,
                "data" : data
            }
            country = country_from_ip(request)[1]
            if country is None:
                lang = 'en'
            else:
                lang = get_country_lang(country)
            response = render(request, "users/country_pick.html", context)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
            return response
    else:
        return redirect("accounts:home", pk=request.user.pk)


# Personal Register
def PersonalSignUp(request, country):
    if request.user.is_anonymous == True:
        ext = phonenumbers.country_code_for_region(country)
        if request.method == "POST":
            form = RegisterForm(request.POST)

            # phone number checking
            phone_num = request.POST.get('phone_number')
            phone_number = phonenumbers.is_valid_number(phonenumbers.parse(f'+{ext}{phone_num}'))
            # print(f'+{ext}{phone_num}')
            if phone_number is False:
                form.add_error('phone_number', _('Please enter a correct phone number'))
                
            if form.is_valid():
                user = {
                    'username'      : form.cleaned_data.get("username"),
                    'email'         : form.cleaned_data.get("email"),
                    'phone_number'  : form.cleaned_data.get("phone_number"),
                    'country'       : country,
                    'password'      : form.cleaned_data.get("password1"),
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
               
                messages.success(
                    request,
                    _(
                        f"Please check your mailbox (as well as spam folder) for a verification code, and enter the 5-digit code below"
                    ),
                )
                return redirect("users:verify-view")
        else:
            form = RegisterForm()
        return render(request, "users/personal.html", {"form": form, "ext" : ext})
    else:
        return redirect("accounts:home", pk=request.user.pk)


# Email Verify 
def email_verify_view(request):
    if request.user.is_anonymous == True:
        user = request.session.get('user')
        form = EmailCodeForm(request.POST or None)
        email_code = request.session.get('ver_code')['email_verify_code']
        if not request.POST:
            # send email
            EMAIL_ID = config.get("EMAIL_ID")
            send_mail(
                _(f"Hello {user['username']}"),
                _(
                    f"Your verification code is : {email_code}, you are very close to starting your money making process!"
                ),
                f"{EMAIL_ID}",
                [f"{user['email']}"],
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
                return redirect("users:phone-verify-view")
            else:
                messages.warning(
                    request,
                    _(f"You enterd the wrong verificaiton code ! Please try again"),
                )
        return render(request, "users/email_verify.html", {"form": form})
    else:
        return redirect("accounts:home", pk=request.user.pk)


# Phone Verify
def phone_verify_view(request):
    if request.user.is_anonymous == True:
        user = request.session.get('user')
        form = PhoneCodeForm(request.POST or None)
        phone_code = request.session.get('ver_code')['phone_verify_code']
        phone_number = user['phone_number']
        if not request.POST:
            # send SMS
            phone_msg_verify(
                verify_code=phone_code, phone_number_to=phone_number
            )
        if form.is_valid():
            num = form.cleaned_data.get("phone_verify_code")
            if str(phone_code) == num:
                if user['iban'] is not None: # checking to see if the user has an iban
                    messages.success(
                        request,
                        _(
                            f"Enter your friend's referral code in order for both of you to get grand prize !"
                        ),
                    )
                    return redirect("users:referral-verify-view")
                else:
                    messages.success(
                        request,
                        _(
                            f"Enter your friend's referral code in order for both of you to get grand prize !"
                        ),
                    )
                    return redirect("users:referral-verify-view")
            else:
                messages.warning(
                    request,
                    _(f"You enterd the wrong verificaiton code ! Please try again"),
                )
        return render(request, "users/phone_verify.html", {"form": form})
    else:
        return redirect("accounts:home", pk=request.user.pk)


# Referral Verify
def referral_verify_view(request, backend='django.contrib.auth.backends.ModelBackend'):
    if request.user.is_anonymous == True:
        # the amount in which new user's bonus will get
        extra_bonus_value = 200

        # getting stuff to sign up the user
        user = request.session.get('user')
        username = user['username']
        password = user['password']
        phone_number = user['phone_number']
        country = user['country']
        phone_ext = phonenumbers.country_code_for_region(country)
        currency = get_country_currency(country)
        language = get_country_lang(country)

        form = ReferralCodeForm(request.POST or None)

        if form.is_valid():
            enterd_code = form.cleaned_data.get("referral_code")
            friend_code = ReferralCode.objects.filter(referral_code=enterd_code)

            if friend_code:  # referral code exists
                # creating a user
                user_ = CustomUser.objects.create(username=username, password=make_password(password), phone_number=phone_number, country=country,
                phone_ext=phone_ext, currency=currency, language=language)
                user_.save()
                login(request, user_, backend)

                # getting current user's stuff
                user_currency           = user_.currency
                user_currency_symbol    = currency_symbol(user_currency) # their currency symbol
                user_currency_min       = currency_min(user_currency)
                user_extra_bonus        = user_currency_min * extra_bonus_value

                # creating an account for the user
                bonus                   = (user_currency_min * 1000) + user_extra_bonus
                user_account = account.objects.create(created_by=user_, bonus=bonus, main_currency=currency, pk=user_.pk)
                user_account.save()

                # updating the user's bonus
                account.objects.filter(created_by=user_).update(bonus = user_extra_bonus + user_currency_min * 1000)

                # getting the some info from the user whose referral code was used
                giver_user = ReferralCode.objects.get(referral_code=enterd_code).user # their name
                giver_account           = account.objects.get(created_by=giver_user) # their account
                giver_balance           = giver_account.total_balance # their balance
                giver_bonus             = giver_account.bonus # their bonus
                giver_currency          = giver_account.main_currency # their currency in iso-3 format
                giver_currency_min      = currency_min(giver_currency) # $1 in their currency
                giver_extra_bonus       = giver_currency_min * extra_bonus_value
                giver_currency_symbol   = currency_symbol(giver_currency) # their currency symbol

                # updating the giver user's bonus
                account.objects.filter(created_by=giver_user).update(
                    bonus = giver_bonus + giver_extra_bonus,
                    total_balance = giver_balance + giver_currency_min
                )

                # send email to the person whose referral code was just used
                EMAIL_ID = config.get("EMAIL_ID")
                GIVER_EMAIL = giver_user.email
                send_mail(
                    _(f"Dear {giver_user.username} !"),
                    _(
                        f"{user['username']} just used your referral code ! You recieved {giver_currency_symbol}{giver_currency_min} on your balance, and {giver_currency_symbol}{giver_extra_bonus} added to your bonus !"
                    ),
                    f"{EMAIL_ID}",
                    [f"{GIVER_EMAIL}"],
                )

                # success message
                messages.success(request,
                    _(f"You have successfully registered, {user['username']}. For your prize, {user_currency_symbol}{user_extra_bonus} has been transfered to your bonus !")
                )

                # redirect to the new user's home page
                return redirect("accounts:home", pk=user_.pk)

            else:  # referral code not entered
                # creating a user
                user_ = CustomUser.objects.create(username=username, password=make_password(password), phone_number=phone_number, country=country,
                phone_ext=phone_ext, currency=currency, language=language)
                user_.save()
                login(request, user_, backend)

                # creating an account for the user
                user_currency_min       = currency_min(user_.currency)
                bonus                   = user_currency_min * 1000
                account.objects.create(created_by=user_, bonus=bonus, main_currency=currency, pk=user_.pk)
                
                # success message
                if enterd_code == "":  # referral code not submitted
                    messages.success(request,
                        _(f"You have successfully registered, {user['username']} !")
                    )
                else: # referral code was wrong
                    messages.success(request,
                        _(f"Sorry, this referral code is incorrect, but you have successfully registered, {user['username']} !")
                    )
                
                # redirect to the new user's home page
                return redirect("accounts:home", pk=user_.pk)
        
        return render(request, "users/referral_code.html", {"form": form})
    else:
        return redirect("accounts:home", pk=request.user.pk)


# Login Page
def LoginClassView(request):
    if request.user.is_anonymous == True:
        form = AuthenticationForm()
        template_name = "users/login.html"
        next = request.GET.get('next')
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page.
                user_language = CustomUser.objects.get(pk=request.user.pk).language
                if next is None:
                    response = redirect("accounts:home", pk=request.user.pk)
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
                    return response
                else:
                    response = redirect(next)
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
                    return response
            else:
                messages.warning(request, _("Please enter a correct username and password. Note that both fields are case-sensitive (Pay attention to capital letters)."))
        return render(request, template_name, {'form' : form})
    else:
        return redirect("accounts:home", pk=request.user.pk)


# cookie policy page
def CookiePolicy(request):
    return render(request, "users/cookie_policy.html")


'''#  DELETE LATER
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
        return redirect("accounts:home", pk=pk request.user.pk})) '''

''' # ajax search through countries
def CountryPicker(request):
    if request.is_ajax():
        typed = request.POST.get('typed')
        
        values = CountryDict(typed.lower())

        if len(values) > 0:
            response = values
        else: # didnt find any countries
            response = "No countries were found."

        return JsonResponse({"data" : response})
    return JsonResponse({}) '''

''' class LoginClassView(LoginView):
    template_name = "users/login.html"

    I commented this out, becuase I want users to be able to be redirected to their specific
    pages after they log in. eg: say someone comes from a shop to /checkout then they have to 
    first login, then be immidietly redirected to that checkout page, by using the login_required 
    decorator, but if i have this get_success_url then it will overwrite the ?next parameter and
    mess up the proccess.

    def get_success_url(self):
        # url = self.get_redirect_url()
        return reverse_lazy(
            "accounts:home", kwargs={"pk": get_current_user().account.pk}
        )'''

''' def iban_verify_view(request):
    if request.user.is_anonymous == True:
        form = IbanCodeForm(request.POST or None)
        pk = request.session.get("pk")
        if pk:
            user = CustomUser.objects.get(pk=pk)
            iban_code = user.code.iban_verify_code
            if not request.POST:
                # send email
                # iban_number = CustomUser.objects.get(pk=pk).iban
                EMAIL_ID = config.get("EMAIL_ID")
                MOE_EMAIL = config.get("MOE_EMAIL")
                send_mail(
                    f"IBAN verficication code for {user.username}",
                    f"The IBAN verification code for user : {user.username} is : {iban_code}",
                    f"{EMAIL_ID}",
                    [f"{MOE_EMAIL}"],
                )
            if form.is_valid():
                num = form.cleaned_data.get("iban_verify_code")
                if str(iban_code) == num:
                    messages.success(
                        request,
                        _(
                            f"Enter your friend's referral code in order for both of you to get grand prize !"
                        ),
                    )
                    return redirect("referral-verify-view")
        return render(request, "users/iban_verify.html", {"form": form})
    else:
        return redirect("accounts:home", pk=pk request.user.pk}))
messages.success(
    request,
    _(
        f"Please wait for our support team to send you a pre-decided amount of money. Check your bank account and then enter the small amount bellow."
    ),
)
return redirect("iban-verify-view") '''

''' # setting cookies 
def cookie_monster(request):
    cookies = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    if cookies is None: # no cookies
        print('NEW cookies', cookies)
        if request.user.is_authenticated == True:
            lang = CustomUser.object.get(pk=request.user.pk).language
            translation.activate(lang)
        else:
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
            EN = ['Canada', 'canada', 'CA', 'ca', 'USA', 'US', 'United States', 'United States of America', 'Australias', 'UK', 'England', 'United Kingdom', 'Jamaica']
            if code in EN:
                code = 'en'
            translation.activate(code)
    else: # cookies exist already
        print("OLD cookies", cookies)
        translation.activate(cookies) '''
