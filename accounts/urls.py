from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views as account_views

app_name = "accounts"
urlpatterns = [
    path("admin/", account_views.AdminRickRoll, name="admin-rick-roll"),
    path("<int:pk>/", account_views.HomeView.as_view(), name="home"),
    path("", account_views.HomeTemplateView.as_view(), name="home-new"),
    path("about/", account_views.AboutTemplateView, name="about-page"),
    path("new_dunc/", account_views.new_dunc),
    path("<int:pk>/transfer/", account_views.TransferCreateView, name="transfer"),
    path("<int:pk>/invite-friends", account_views.ReferralCodeView, name="referral-code"),
    path("<int:pk>/add_money/", account_views.AddMoneyUpdateView, name="add-money"),
    path("<int:pk>/take_money/", account_views.TakeMoneyUpdateView, name="take-money"),
    path("<int:pk>/deposit-info/", account_views.AddMoneyInfo, name="add-money-info"),
    path("<int:pk>/history/", account_views.History, name="history"),
    path("<int:pk>/cash_out/", account_views.cash_out, name="cash-out"),
    path("payment/<str:url1>/<str:url2>/<str:url3>/<str:url4>/", account_views.payment, name="payment"),
    path("payment/<str:url1>/<str:url2>/<str:url3>/<str:url4>/<str:price>/payment_done/", account_views.payment_done, name="payment-done"),
    path("checkout/<str:shop>/<str:price>/", account_views.checkout, name="checkout"),
    path("checkout/<str:shop>/<str:price>/checkout_complete", account_views.checkout_complete, name="checkout-complete")
]

# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
