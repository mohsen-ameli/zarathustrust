from django.contrib.auth import views as auth_views
from django.urls import path
from . import views as users_views

app_name = "users"
urlpatterns = [
    # Matrix
    path("matrix/", users_views.Matrix, name="matrix"),

    # cookies
    path("cookie-policy/", users_views.CookiePolicy, name="cookie-policy"),

    # login/out
    path("login/", users_views.LoginClassView, name="login-view"),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"),

    # register
    path("register/", users_views.register, name="register"),
    path("register/business/", users_views.business, name="business"),
    path("register/personal/", users_views.PersonalCountryPickSignUp, name="personal-country-pick"),
    path("register/personal/<str:country>/", users_views.PersonalSignUp, name="personal-sign-up"),

    # verifying
    path("email-verify/", users_views.email_verify_view, name="verify-view"),
    path("phone-verify/", users_views.phone_verify_view, name="phone-verify-view"),
    path("referral-code/", users_views.referral_verify_view, name="referral-verify-view"),
]

# path("login/<str:url1>/<str:url2>/<str:url3>/<str:url4>/", users_views.auth_view, name="login-view-pay"),