from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import random

from users.models import CustomUser, OneTimePassword
from users.serializers import PhoneSerializer, OTPVerifySerializer, RegistrationCompleteSerializer, LoginSerializer, \
    ProfileSerializer

class CheckPhoneView(APIView):
    permission_classes = []

    @extend_schema(
        description="Проверить, существует ли пользователь с данным номером",
        request=PhoneSerializer,
        responses={
            status.HTTP_200_OK: {
                "description": "Результат проверки номера",
                "type": "object",
                "properties": {
                    "exists": {"type": "boolean", "description": "True, если номер найден в БД"},
                    "next": {"type": "string", "description": "Следующий шаг: 'login' или 'register'"}
                }
            },
            status.HTTP_400_BAD_REQUEST: "Некорректный номер телефона"
        }
    )
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone_number']
        exists = CustomUser.objects.filter(phone_number=phone).exists()
        action = 'login' if exists else 'register'


        return Response(
            {"exists": exists, "next": action},
            status=status.HTTP_200_OK
        )


class SendOTPView(APIView):
    permission_classes = []

    @extend_schema(
        description="Отправить одноразовый код (OTP) на указанный номер телефона",
        request=PhoneSerializer,
        responses={
            status.HTTP_200_OK: {
                "description": "Код успешно отправлен",
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "description": "True, если код успешно отправлен"},
                    "message": {"type": "string", "description": "Сообщение о результате операции"}
                }
            },
            status.HTTP_400_BAD_REQUEST: "Некорректный номер телефона"
        }
    )
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone_number']
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        OneTimePassword.objects.create(
            phone_number=phone,
            code=otp_code,
        )

        return Response(
            {
                "success": True,
                "message": "Код подтверждения был отправлен успешно",
                # TODO: Remove in prod
                "debug_otp": otp_code
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    permission_classes = []

    @extend_schema(
        description="Проверить код подтверждения (OTP)",
        request=OTPVerifySerializer,
        responses={
            status.HTTP_200_OK: {
                "description": "Результат проверки кода",
                "type": "object",
                "properties": {
                    "verified": {"type": "boolean", "description": "True, если код верный и не истек срок действия"},
                    "message": {"type": "string", "description": "Сообщение о результате операции"}
                }
            },
            status.HTTP_400_BAD_REQUEST: "Некорректные данные или истекший код"
        }
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        try:
            otp = OneTimePassword.objects.filter(
                phone_number=phone
            ).latest('created_at')

            if code != str(otp.code):
                return Response(
                    data={
                        "success": False,
                        "message": "Неверный код подтверждения"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            expiry = otp.created_at + timedelta(minutes=1)
            if expiry < timezone.now():
                return Response(
                    {
                        "success": False,
                        "message": "Срок действия кода истёк"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    "success": True,
                    "message": "Код подтверждения верный"
                },
                status=status.HTTP_200_OK
            )

        except OneTimePassword.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Код подтверждения не найден"
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterUserView(APIView):
    permission_classes = []

    @extend_schema(
        description="Зарегистрировать нового пользователя с подтвержденным номером телефона",
        request=RegistrationCompleteSerializer,
        responses={
            status.HTTP_201_CREATED: {
                "description": "Пользователь успешно зарегистрирован",
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "description": "JWT Refresh Token"},
                    "access": {"type": "string", "description": "JWT Access Token"}
                }
            },
            status.HTTP_400_BAD_REQUEST: "Некорректные данные или пользователь уже существует"
        }
    )
    def post(self, request):
        serializer = RegistrationCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']
        password2 = serializer.validated_data['password2']
        first_name = serializer.validated_data.get('first_name', '')
        last_name = serializer.validated_data.get('last_name', '')

        if password != password2:
            return Response(
                {
                    "success": False,
                    "message": "Пароли не совпадают"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            return Response(
                {
                    "success": False,
                    "message": "Пользователь с таким номером телефона уже существует"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = CustomUser.objects.create_user(
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = []

    @extend_schema(
        description="Войти по номеру телефона и паролю, получить JWT-токены",
        request=LoginSerializer,
        responses={
            status.HTTP_200_OK: {
                "description": "Успешная аутентификация",
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "description": "JWT Refresh Token"},
                    "access": {"type": "string", "description": "JWT Access Token"}
                }
            },
            status.HTTP_401_UNAUTHORIZED: "Неверные учётные данные"
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        user = authenticate(request, phone_number=phone, password=password)
        if user is None:
            return Response(
                {"detail": "Неверный номер или пароль"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            },
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Получить данные профиля текущего пользователя",
        responses={status.HTTP_200_OK: ProfileSerializer}
    )
    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data)
    
    @extend_schema(
        description="Обновить данные профиля текущего пользователя",
        request=ProfileSerializer,
        responses={
            status.HTTP_200_OK: ProfileSerializer,
            status.HTTP_400_BAD_REQUEST: "Incorrect data"
        }
    )
    def patch(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def health_check(request):
    return Response({"status": "OK"})