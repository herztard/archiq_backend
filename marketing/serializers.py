from drf_spectacular.utils import extend_schema_field, OpenApiTypes
from rest_framework import serializers
from .models import Banner

class BannerCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)

    class Meta:
        model = Banner
        fields = (
            "title",
            "subtitle",
            "target_url",
            "start_at",
            "end_at",
            "image",
        )

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"
        read_only_fields = ("id", "image_link")
