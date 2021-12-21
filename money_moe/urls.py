from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from users import views as users_views

app_name = "money_moe"
urlpatterns = [
    path("", include("accounts.urls"), name="home"),
    path("g0atch33se&pizz1/", admin.site.urls, name="admin"),
    path("register/", users_views.register, name="register"),
    path("register/personal/", users_views.personal, name="personal"),
    path("register/business/", users_views.business, name="business"),
    path("login/<str:url1>/<str:url2>/<str:url3>/<str:url4>/", users_views.auth_view, name="login-view-pay"),
    path("login/", users_views.LoginClassView, name="login-view"),
    path("email-verify/", users_views.email_verify_view, name="verify-view"),
    path("phone-verify/", users_views.phone_verify_view, name="phone-verify-view"),
    path("iban-verify/", users_views.iban_verify_view, name="iban-verify-view"),
    path("referral-code/", users_views.referral_verify_view, name="referral-verify-view"),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html"), name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"),name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete"),
]

urlpatterns += i18n_patterns(path("i18n/", include("django.conf.urls.i18n")))

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]


# path("login/", users_views.LoginClassView.as_view(redirect_authenticated_user=True), name="login-view"),