# users/urls.py

from django.urls import path
from .views import (
    CheckPhoneView,
)

urlpatterns = [
    path('auth/check-phone/', CheckPhoneView.as_view(), name='check-phone'),
]
