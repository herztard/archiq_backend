from datetime import timedelta

from django.contrib.auth.models import AbstractUser, PermissionsMixin, Group, Permission
from django.core.validators import RegexValidator
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from users.managers import CustomUserManager


class CustomUser(AbstractUser, PermissionsMixin):
    PHONE_REGEX = RegexValidator(
        regex=r'^+7\d{10}$',
        message="Номер телефона должен быть в формате +7XXXXXXXXXX (11 цифр), без знака +"
    )

    username = None
    phone_number = PhoneNumberField(null=False, blank=True, unique=True, region='KZ', help_text='Введите номер в формате +77xxxxxxxxx')

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"User #{self.id}: {self.phone_number}, {self.first_name} {self.last_name}"

    groups = models.ManyToManyField(Group, blank=True, related_name="user_set")

    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="user_set")

    class Meta:
        db_table = 'users'

class OneTimePassword(models.Model):
    phone_number = PhoneNumberField(null=False, blank=False)
    code = models.CharField(max_length=6, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.phone_number}: {self.code}"

    class Meta:
        db_table = "onetime_passwords"
