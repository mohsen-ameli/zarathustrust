from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logoutView, name='logout'),
    
    path('signup/', signUp, name='sign-up'),
    path('verify-email/', verifyEmail, name='verify-email'),
    path('verify-phone/', verifyPhone, name='verify-phone'),
    path('verify-referral/', verifyReferral, name='verify-referral'),

    path('password-reset/', RequestPasswordResetEmail.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordTokenCheck.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', PasswordResetAPIView.as_view(), name='password-complete'),
]