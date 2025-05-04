from django.http import Http404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import Banner
from .serializers import BannerCreateSerializer, BannerSerializer
from .permissions import AllowAnyListGet, IsAdminOrManager
from clients.s3 import S3Client, generate_unique_filename
from django.conf import settings

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
