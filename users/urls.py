# users/urls.py

from django.urls import path
from .views import (
    CheckPhoneView,
    SendOTPView,
    VerifyOTPView,
    RegisterUserView, LoginView,
)

urlpatterns = [
    path('auth/check-phone/', CheckPhoneView.as_view(), name='check-phone'),
    path('auth/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path("auth/login/", LoginView.as_view(), name="login"),
]
