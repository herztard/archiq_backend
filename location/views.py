from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import City, District
from .serializers import (
    CitySerializer, CityWithDistrictsSerializer,
    DistrictSerializer, DistrictDetailSerializer
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
    
    @extend_schema(
        request=CitySerializer,
        responses={status.HTTP_201_CREATED: CitySerializer}
    )
    def post(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CityDetailView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get_object(self, pk):
        return get_object_or_404(City, pk=pk)
    
    @extend_schema(
        responses={status.HTTP_200_OK: CityWithDistrictsSerializer}
    )
    def get(self, request, pk):
        city = self.get_object(pk)
        serializer = CityWithDistrictsSerializer(city)
        return Response(serializer.data)
    
    @extend_schema(
        request=CitySerializer,
        responses={status.HTTP_200_OK: CitySerializer}
    )
    def put(self, request, pk):
        city = self.get_object(pk)
        serializer = CitySerializer(city, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        request=CitySerializer,
        responses={status.HTTP_200_OK: CitySerializer}
    )
    def patch(self, request, pk):
        city = self.get_object(pk)
        serializer = CitySerializer(city, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        city = self.get_object(pk)
        city.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        
        # Filter by city_id if provided
        city_id = request.query_params.get('city')
        if city_id and city_id.isdigit():
            districts = districts.filter(city_id=int(city_id))
            
        serializer = DistrictSerializer(districts, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=DistrictSerializer,
        responses={status.HTTP_201_CREATED: DistrictSerializer}
    )
    def post(self, request):
        serializer = DistrictSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DistrictDetailView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get_object(self, pk):
        return get_object_or_404(District, pk=pk)
    
    @extend_schema(
        responses={status.HTTP_200_OK: DistrictDetailSerializer}
    )
    def get(self, request, pk):
        district = self.get_object(pk)
        serializer = DistrictDetailSerializer(district)
        return Response(serializer.data)
    
    @extend_schema(
        request=DistrictSerializer,
        responses={status.HTTP_200_OK: DistrictSerializer}
    )
    def put(self, request, pk):
        district = self.get_object(pk)
        serializer = DistrictSerializer(district, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        request=DistrictSerializer,
        responses={status.HTTP_200_OK: DistrictSerializer}
    )
    def patch(self, request, pk):
        district = self.get_object(pk)
        serializer = DistrictSerializer(district, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        district = self.get_object(pk)
        district.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
