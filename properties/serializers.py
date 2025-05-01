from rest_framework import serializers
from .models import ResidentialComplex, ResidentialComplexPhotos, Block, Property, PropertyPhotos, PropertyVideos
from location.models import District
from clients.s3 import S3Client, generate_unique_filename
from django.conf import settings


class PropertyPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyPhotos
        fields = ['id', 'photo_link']


class PropertyPhotoCreateSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(write_only=True)
    photo_link = serializers.URLField(read_only=True)
    
    class Meta:
        model = PropertyPhotos
        fields = ['photo', 'photo_link']
    
    def create(self, validated_data):
        photo_file = validated_data.pop('photo')
        property_instance = validated_data.get('property')
        
        unique_name = generate_unique_filename(photo_file.name)
        destination = f"property_photos/{unique_name}"
        
        s3 = S3Client()
        photo_file.seek(0)
        s3.upload_to_s3(file_content=photo_file.read(), destination_blob_name=destination)
        
        photo_link = f"{settings.AWS_S3_FULL_URL}/{destination}"
        
        return PropertyPhotos.objects.create(
            property=property_instance,
            photo_link=photo_link
        )


class PropertyVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideos
        fields = ['id', 'video_link']


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']


class BlockSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'block_number', 'entrance_number', 'total_floors', 'building_status']


class ResidentialComplexSimpleSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    
    class Meta:
        model = ResidentialComplex
        fields = ['id', 'name', 'address', 'class_type', 'district']


class PropertySerializer(serializers.ModelSerializer):
    property_photos = PropertyPhotosSerializer(many=True, read_only=True)
    property_videos = PropertyVideosSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    block_id = serializers.IntegerField(write_only=True, required=True)
    block = BlockSimpleSerializer(read_only=True)
    complex = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'category', 'number', 'price', 'price_per_sqm', 'rental_price',
            'floor', 'area', 'rooms', 'renovation_type', 'wall_material',
            'layout', 'description', 'entrance', 'property_photos', 'property_videos',
            'block_id', 'block', 'complex'
        ]
        read_only_fields = ['price', 'block', 'complex']
    
    def get_price(self, obj):
        if obj.area and obj.price_per_sqm:
            return float(obj.area) * float(obj.price_per_sqm)
        return obj.price
    
    def get_complex(self, obj):
        return ResidentialComplexSimpleSerializer(obj.block.complex).data
    
    def validate(self, data):
        # Calculate price automatically from area and price_per_sqm
        if 'area' in data and 'price_per_sqm' in data:
            data['price'] = data['area'] * data['price_per_sqm']
        elif 'area' in data and self.instance and self.instance.price_per_sqm:
            data['price'] = data['area'] * self.instance.price_per_sqm
        elif 'price_per_sqm' in data and self.instance and self.instance.area:
            data['price'] = self.instance.area * data['price_per_sqm']
        return data


class PropertyDetailSerializer(serializers.ModelSerializer):
    property_photos = PropertyPhotosSerializer(many=True, read_only=True)
    property_videos = PropertyVideosSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    block = BlockSimpleSerializer(read_only=True)
    complex = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'category', 'number', 'price', 'price_per_sqm', 'rental_price',
            'floor', 'area', 'rooms', 'renovation_type', 'wall_material',
            'layout', 'description', 'entrance', 'property_photos', 'property_videos',
            'block', 'complex'
        ]
        read_only_fields = ['price', 'block', 'complex']
    
    def get_price(self, obj):
        if obj.area and obj.price_per_sqm:
            return float(obj.area) * float(obj.price_per_sqm)
        return obj.price
    
    def get_complex(self, obj):
        return ResidentialComplexSimpleSerializer(obj.block.complex).data
    
    def validate(self, data):
        if 'area' in data and 'price_per_sqm' in data:
            data['price'] = data['area'] * data['price_per_sqm']
        elif 'area' in data and self.instance and self.instance.price_per_sqm:
            data['price'] = data['area'] * self.instance.price_per_sqm
        elif 'price_per_sqm' in data and self.instance and self.instance.area:
            data['price'] = self.instance.area * data['price_per_sqm']
        return data


class BlockSerializer(serializers.ModelSerializer):
    complex_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Block
        fields = [
            'id', 'block_number', 'entrance_number', 'total_floors', 'queue',
            'deadline_year', 'deadline_querter', 'total_apartments',
            'building_status', 'link_on_map', 'complex_id'
        ]


class ResidentialComplexPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentialComplexPhotos
        fields = ['id', 'photo_link']


class ResidentialComplexPhotoCreateSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(write_only=True)

    class Meta:
        model = ResidentialComplexPhotos
        fields = ['photo']
    
    def create(self, validated_data):
        photo_file = validated_data.pop('photo')
        complex = validated_data.get('complex')
        
        unique_name = generate_unique_filename(photo_file.name)
        destination = f"residential_complex_photos/{unique_name}"
        
        s3 = S3Client()
        photo_file.seek(0)
        s3.upload_to_s3(file_content=photo_file.read(), destination_blob_name=destination)
        
        photo_link = f"{settings.AWS_S3_FULL_URL}/{destination}"
        
        return ResidentialComplexPhotos.objects.create(
            complex=complex,
            photo_link=photo_link
        )


class ResidentialComplexListSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    residential_complex_photos = ResidentialComplexPhotosSerializer(many=True, read_only=True)
    
    class Meta:
        model = ResidentialComplex
        fields = [
            'id', 'name', 'address', 'class_type', 'district',
            'residential_complex_photos', 'description_short'
        ]


class ResidentialComplexDetailSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    blocks = BlockSerializer(many=True, read_only=True)
    residential_complex_photos = ResidentialComplexPhotosSerializer(many=True, read_only=True)
    
    class Meta:
        model = ResidentialComplex
        fields = [
            'id', 'name', 'address', 'class_type', 'construction_technology',
            'heating_type', 'has_elevator_pass', 'has_elevator_cargo',
            'ceiling_height', 'block_number', 'down_payment', 'installment_plan',
            'latitude', 'longitude', 'link_on_map', 'description_full',
            'description_short', 'created_at', 'district', 'blocks',
            'residential_complex_photos'
        ]


class ResidentialComplexCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentialComplex
        fields = [
            'id', 'name', 'address', 'class_type', 'construction_technology',
            'heating_type', 'has_elevator_pass', 'has_elevator_cargo',
            'ceiling_height', 'block_number', 'down_payment', 'installment_plan',
            'latitude', 'longitude', 'link_on_map', 'description_full',
            'description_short', 'district'
        ]
    
    def create(self, validated_data):
        photos_data = validated_data.pop('residential_complex_photos', [])
        complex = ResidentialComplex.objects.create(**validated_data)
        
        for photo_data in photos_data:
            photo_data['complex'] = complex
            photo_serializer = ResidentialComplexPhotoCreateSerializer(data=photo_data)
            if photo_serializer.is_valid(raise_exception=True):
                photo_serializer.save(complex=complex)
            
        return complex
    
    def update(self, instance, validated_data):
        photos_data = validated_data.pop('residential_complex_photos', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        for photo_data in photos_data:
            photo_data['complex'] = instance
            photo_serializer = ResidentialComplexPhotoCreateSerializer(data=photo_data)
            if photo_serializer.is_valid(raise_exception=True):
                photo_serializer.save(complex=instance)
            
        return instance
