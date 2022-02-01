from django.contrib.auth import views as auth_views
from django.urls import path
from . import views as users_views

app_name = "users"
urlpatterns = [
    path("cookie-policy/", users_views.CookiePolicy, name="cookie-policy"),

    path("register/", users_views.register, name="register"),
    path("register/business/", users_views.business, name="business"),
    path("register/personal/", users_views.PersonalCountryPickSignUp, name="personal-country-pick"),
    path("register/personal/<str:country>/", users_views.PersonalSignUp, name="personal-sign-up"),

    path("email-verify/", users_views.email_verify_view, name="verify-view"),
    path("phone-verify/", users_views.phone_verify_view, name="phone-verify-view"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"),name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete"),

    path("login/", users_views.LoginClassView, name="login-view"),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"),

    path("referral-code/", users_views.referral_verify_view, name="referral-verify-view"),
]

# path("login/<str:url1>/<str:url2>/<str:url3>/<str:url4>/", users_views.auth_view, name="login-view-pay"),