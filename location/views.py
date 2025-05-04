from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import City, District
from .serializers import (
    CitySerializer,
    DistrictSerializer,
)
from properties.permissions import ReadOnlyForAnyone


class CityListView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    @extend_schema(
        responses={status.HTTP_200_OK: CitySerializer(many=True)}
    )
    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)

class DistrictListView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="city", description="Filter by city ID", type=OpenApiTypes.INT, required=False),
        ],
        responses={status.HTTP_200_OK: DistrictSerializer(many=True)}
    )
    def get(self, request):
        districts = District.objects.all()
        
        city_id = request.query_params.get('city')
        if city_id and city_id.isdigit():
            districts = districts.filter(city_id=int(city_id))
            
        serializer = DistrictSerializer(districts, many=True)
        return Response(serializer.data)