from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from users import views as users_views

app_name = "money_moe"
urlpatterns = [
    path("", include("accounts.urls"), name="home"),
    path("", include("users.urls"), name="users"),
    path("", include("wallets.urls"), name="wallets"),
    path('captcha/', include('captcha.urls')),

    path("g0atch33se&pizz1/", admin.site.urls, name="admin"),
]

urlpatterns += i18n_patterns(path("i18n/", include("django.conf.urls.i18n")))

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]
