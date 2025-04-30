from django.http import Http404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .models import Banner
from .serializers import BannerCreateSerializer, BannerSerializer
from .permissions import AllowAnyListGet, IsAdminOrManager
from clients.s3 import S3Client, generate_unique_filename
from archiq_backend.settings import (
    AWS_S3_ENDPOINT_URL,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_CUSTOM_DOMAIN, AWS_S3_FULL_URL,
)

class ActionMixin:
    def initial(self, request, *args, **kwargs):
        if request.method == 'GET' and not kwargs:
            self.action = 'list'
        else:
            self.action = None
        return super().initial(request, *args, **kwargs)
class BannerListCreateView(ActionMixin, APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAnyListGet]

    @extend_schema(
        description="Получить список всех баннеров",
        responses={status.HTTP_200_OK: BannerSerializer(many=True)},
    )
    def get(self, request):
        curr_date = timezone.now()
        banners = Banner.objects.filter(start_at__lt=curr_date, end_at__gt=curr_date).all()
        serializer = BannerSerializer(banners, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Создать новый баннер (multipart/form-data)",
        request=BannerCreateSerializer,
        responses={status.HTTP_201_CREATED: BannerSerializer},
    )
    def post(self, request):
        create_serializer = BannerCreateSerializer(data=request.data)
        if not create_serializer.is_valid():
            return Response(create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = create_serializer.validated_data
        image_file = data.pop("image", None)
        if not image_file:
            return Response(
                data={
                    "success": False,
                    "message": "Пожалуйста, загрузите картинку баннера"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        unique_name = generate_unique_filename(image_file.name)
        destination = f"{AWS_S3_FULL_URL}/banner/{unique_name}"
        s3 = S3Client()
        image_file.seek(0)
        s3.upload_to_s3(file_content=image_file.read(), destination_blob_name=destination)
        banner = Banner.objects.create(image_link=destination, **data)
        out = BannerSerializer(banner)
        return Response(out.data, status=status.HTTP_201_CREATED)


class BannerDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminOrManager]

    def get_object(self, pk):
        try:
            return Banner.objects.get(pk=pk)
        except Banner.DoesNotExist:
            raise Http404

    @extend_schema(
        description="Получить конкретный баннер",
        responses={status.HTTP_200_OK: BannerSerializer},
    )
    def get(self, request, pk):
        banner = self.get_object(pk)
        return Response(BannerSerializer(banner).data)

    @extend_schema(
        description="Полностью обновить баннер",
        request=BannerCreateSerializer,
        responses={status.HTTP_200_OK: BannerSerializer},
    )
    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    @extend_schema(
        description="Частично обновить баннер",
        request=BannerCreateSerializer,
        responses={status.HTTP_200_OK: BannerSerializer},
    )
    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        banner = self.get_object(pk)
        create_ser = BannerCreateSerializer(data=request.data, partial=partial)
        if not create_ser.is_valid():
            return Response(create_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        data = create_ser.validated_data
        if "image" in data:
            image_file = data.pop("image")
            unique_name = generate_unique_filename(image_file.name)
            S3Client().upload_to_s3(image_file.read(), unique_name)
            if AWS_S3_CUSTOM_DOMAIN:
                data["image_link"] = f"https://{AWS_S3_CUSTOM_DOMAIN}/banner/{unique_name}"
            else:
                data["image_link"] = (
                    f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/"
                    f"{AWS_STORAGE_BUCKET_NAME}/{unique_name}"
                )

        # copy other fields onto the instance
        for attr, val in data.items():
            setattr(banner, attr, val)
        banner.save()
        return Response(BannerSerializer(banner).data)
