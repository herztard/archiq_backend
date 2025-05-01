from rest_framework import serializers
from .models import City, District


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'description', 'city']


class DistrictDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'description', 'city']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class CityWithDistrictsSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'districts'] 