import json
from typing import Counter

from accounts.models import account
from crum import get_current_user
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _

from .forms import (
    BusinessForm,
    EmailCodeForm,
    IbanCodeForm,
    PhoneCodeForm,
    ReferralCodeForm,
    RegisterForm,
)
from .models import CustomUser, code
from .utils import phone_msg_verify

with open("/etc/config.json") as config_file:
    config = json.load(config_file)


def register(request):
    return render(request, "users/register.html")


def business(request):
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
                return redirect("/")
            else:
                # Return an 'invalid login' error message.
                return redirect("/")
    else:
        form = BusinessForm()
    return render(request, "users/business.html", {"form": form})


def personal(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user_ = authenticate(request, username=username, password=password)
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
    return render(request, "users/personal.html", {"form": form})


def email_verify_view(request):
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
            print(email_code)
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


def phone_verify_view(request):
    form = PhoneCodeForm(request.POST or None)
    pk = request.session.get("pk")
    if pk:
        user = CustomUser.objects.get(pk=pk)
        phone_code = user.code.phone_verify_code
        if not request.POST:
            # send SMS
            phone_ext = CustomUser.objects.get(pk=pk).phone_ext
            phone_number = CustomUser.objects.get(pk=pk).phone_number
            phone_msg_verify(
                verify_code=phone_code, phone_number_to=phone_ext + phone_number
            )
            print(phone_code)
        if form.is_valid():
            num = form.cleaned_data.get("phone_verify_code")
            if str(phone_code) == num:
                if CustomUser.objects.get(pk=pk).iban != "":
                    messages.success(
                        request,
                        _(
                            f"Please wait for our support team to send you a pre-decided amount of money. Check your bank account and then enter the small amount bellow."
                        ),
                    )
                    return redirect("iban-verify-view")
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


def iban_verify_view(request):
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
            print(iban_code)
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


def referral_verify_view(request):
    form = ReferralCodeForm(request.POST or None)
    pk = request.session.get("pk")
    if pk:
        user = CustomUser.objects.get(pk=pk)
        if form.is_valid():
            enterd_code = form.cleaned_data.get("referral_code")
            friend_code = code.objects.all().filter(referral_code=enterd_code)
            if friend_code:  # referral code exists
                user.code.save()
                login(request, user)

                account.objects.create(created_by=user, total_balance=0, bonus=1200)
                giver_name = code.objects.get(referral_code=enterd_code).user
                new_bal = account.objects.get(created_by=giver_name).total_balance
                ref = account.objects.get(created_by=giver_name).bonus
                account.objects.filter(created_by=giver_name).update(
                    total_balance=new_bal + 1
                )
                account.objects.filter(created_by=giver_name).update(bonus=ref + 200)
                # send email
                EMAIL_ID = config.get("EMAIL_ID")
                GIVER_EMAIL = CustomUser.objects.get(username=user).email
                send_mail(
                    _(f"Dear {giver_name} !"),
                    _(
                        f"{user} just used your referral code ! You recieved $1 on your balance, and $200 added to your bonus !"
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
                login(request, user)
                account.objects.create(created_by=user, total_balance=0)
                messages.success(
                    request, _(f"You have successfully registered, {user.username} !")
                )
                return redirect(
                    reverse("accounts:home", kwargs={"pk": user.account.pk})
                )
            else:  # referral code incorrect
                user.code.save()
                login(request, user)
                account.objects.create(created_by=user, total_balance=0)
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


def auth_view(request, url1, url2, url3, url4):
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


# class LoginClassView(LoginView):
#     template_name = "users/login.html"

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


def LoginClassView(request):
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
            return redirect(reverse("accounts:home", kwargs={"pk" : get_current_user().pk}))
        else:
            messages.warning(request, _("Please enter a correct username and password. Note that both fields are case-sensitive."))
    elif request.method == 'POST' and next is not None:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect(next)
    return render(request, template_name, {'form' : form})