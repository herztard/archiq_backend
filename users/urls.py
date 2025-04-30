# users/urls.py

from django.urls import path
from .views import (
    CheckPhoneView,
    SendOTPView,
    VerifyOTPView,
    RegisterUserView, LoginView, ProfileView,
)

urlpatterns = [
    path('accounts/check-phone/', CheckPhoneView.as_view(), name='check-phone'),
    path('accounts/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('accounts/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path("accounts/login/", LoginView.as_view(), name="login"),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
]
