from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from users.serializers import PhoneSerializer


# Create your views here.
class CheckPhoneView(APIView):
    permission_classes = []  # разрешаем анонимный доступ

    @swagger_auto_schema(
        operation_description="Проверить, существует ли пользователь с данным номером",
        request_body=PhoneSerializer,
        responses={
            200: openapi.Response(
                description="Результат проверки номера",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "exists": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            description="True, если номер найден в БД"
                        ),
                        "next": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Следующий шаг: 'login' или 'register'"
                        )
                    }
                )
            ),
            400: "Некорректный номер телефона"
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

