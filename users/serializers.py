import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import CustomUser, OneTimePassword

OTP_TTL = timedelta(minutes=10)


class PhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True, region='KZ')


class OTPVerifySerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True, region='KZ')
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        cutoff = timezone.now() - OTP_TTL
        otp_qs = OneTimePassword.objects.filter(
            phone_number=data['phone_number'],
            code=data['code'],
            created_at__gte=cutoff
        )
        if not otp_qs.exists():
            raise serializers.ValidationError("OTP is invalid or has expired.")
        return data


class RegistrationCompleteSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True, region='KZ')
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match.")
        if CustomUser.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError("User already exists.")
        return data

    def create(self, validated):
        user = CustomUser.objects.create_user(
            phone_number=validated['phone_number'],
            password=validated['password']
        )
        return user

    def to_representation(self, instance):
        token, _ = Token.objects.get_or_create(user=instance)
        return {'token': token.key}


class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True, region='KZ')
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            phone_number=data['phone_number'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        data['user'] = user
        return data

    def to_representation(self, validated):
        token, _ = Token.objects.get_or_create(user=validated['user'])
        return {'token': token.key}


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True, region='KZ')

    def validate_phone_number(self, phone):
        if not CustomUser.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError("No user with this phone.")
        return phone


class ForgotCompleteSerializer(RegistrationCompleteSerializer):
    def validate(self, data):
        super().validate(data)
        if not CustomUser.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError("User does not exist.")
        return data

    def save(self):
        user = CustomUser.objects.get(phone_number=self.validated_data['phone_number'])
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        # Expect context['request'].user
        super().__init__(*args, **kwargs)
        self.user = self.context['request'].user

    def validate_old_password(self, old):
        if not self.user.check_password(old):
            raise serializers.ValidationError("Wrong old password.")
        return old

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def save(self):
        self.user.set_password(self.validated_data['password'])
        self.user.save()
        return self.user
