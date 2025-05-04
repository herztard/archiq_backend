from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from drf_spectacular.utils import extend_schema_field, OpenApiExample

from .models import Application


class AuthenticatedApplicationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Application
        fields = [
            'id', 'property', 'residential_complex', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        name = f"{user.first_name} {user.last_name}".strip()
        return Application.objects.create(
            user=user, 
            name=name if name else None,
            phone_number=user.phone_number,
            **validated_data
        )


class UnauthenticatedApplicationSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(
        required=True,
        help_text="Phone number in format +7XXXXXXXXXX"
    )
    name = serializers.CharField(
        required=True,
        help_text="Full name of the applicant"
    )
    
    class Meta:
        model = Application
        fields = [
            'id', 'name', 'phone_number', 'property', 
            'residential_complex', 'status', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class ApplicationListSerializer(serializers.ModelSerializer):
    property_details = serializers.SerializerMethodField()
    residential_complex_details = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'user', 'name', 'phone_number', 
            'property', 'property_details',
            'residential_complex', 'residential_complex_details',
            'status', 'created_at', 'updated_at'
        ]
    
    @extend_schema_field(serializers.CharField())
    def get_name(self, obj):
        if obj.user and (obj.name is None or obj.name == ''):
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.phone_number
        return obj.name
    
    @extend_schema_field(serializers.CharField())
    def get_phone_number(self, obj):
        if obj.user and (obj.phone_number is None or str(obj.phone_number) == ''):
            return str(obj.user.phone_number)
        return str(obj.phone_number) if obj.phone_number else None
    
    @extend_schema_field(serializers.DictField())
    def get_property_details(self, obj):
        if obj.property:
            return {
                'id': obj.property.id,
                'category': obj.property.category,
                'number': obj.property.number,
                'price': obj.property.price,
                'area': obj.property.area,
                'rooms': obj.property.rooms,
            }
        return None
    
    @extend_schema_field(serializers.DictField())
    def get_residential_complex_details(self, obj):
        if obj.residential_complex:
            return {
                'id': obj.residential_complex.id,
                'name': obj.residential_complex.name,
                'address': obj.residential_complex.address,
            }
        return None 