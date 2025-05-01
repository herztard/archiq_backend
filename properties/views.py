from django.db.models import Min, Max, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import ResidentialComplex, Block, Property, ResidentialComplexPhotos, PropertyPhotos, PropertyVideos
from .serializers import (
    ResidentialComplexListSerializer, ResidentialComplexDetailSerializer,
    ResidentialComplexCreateUpdateSerializer, BlockSerializer, PropertySerializer,
    PropertyDetailSerializer, PropertyPhotosSerializer, PropertyVideosSerializer,
    ResidentialComplexPhotosSerializer, PropertyPhotoCreateSerializer, ResidentialComplexPhotoCreateSerializer,
)
from .permissions import ReadOnlyForAnyone


class ResidentialComplexListView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="available_only", description="Filter by availability (true/false)", type=OpenApiTypes.BOOL, required=False),
            OpenApiParameter(name="district", description="Filter by district ID", type=OpenApiTypes.INT, required=False),
            OpenApiParameter(name="property_category", description="Filter by property category (APARTMENT, PARKING, BOXROOM, COMMERCE)", type=str, enum=["APARTMENT", "PARKING", "BOXROOM", "COMMERCE"], required=False),
            OpenApiParameter(name="class_type", description="Filter by class type (for APARTMENT category)", type=str, enum=["STANDARD", "COMFORT", "BUSINESS", "PREMIUM"], required=False),
            OpenApiParameter(name="rooms", description="Filter by number of rooms (for APARTMENT category)", type=OpenApiTypes.INT, required=False),
            OpenApiParameter(name="min_floor", description="Filter by minimum floor (for APARTMENT category)", type=OpenApiTypes.INT, required=False),
            OpenApiParameter(name="max_floor", description="Filter by maximum floor (for APARTMENT category)", type=OpenApiTypes.INT, required=False),
            OpenApiParameter(name="min_area", description="Filter by minimum area", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="max_area", description="Filter by maximum area", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="min_total_price", description="Filter by minimum total price", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="max_total_price", description="Filter by maximum total price", type=OpenApiTypes.NUMBER, required=False),
        ]
    )
    def get(self, request):
        queryset = ResidentialComplex.objects.all().prefetch_related(
            'residential_complex_photos', 'blocks', 'blocks__properties',
            'district'
        ).order_by('name')
        
        available_only = request.query_params.get('available_only', 'false').lower() == 'true'
        if available_only:
            queryset = queryset.filter(blocks__properties__isnull=False).distinct()

        district_id = request.query_params.get('district')
        if district_id and district_id.isdigit():
            queryset = queryset.filter(district_id=int(district_id))

        property_category = request.query_params.get('property_category')
        if property_category:
            queryset = queryset.filter(blocks__properties__category=property_category).distinct()

            if property_category == 'APARTMENT':
                class_type = request.query_params.get('class_type')
                if class_type:
                    queryset = queryset.filter(class_type=class_type)

                rooms = request.query_params.get('rooms')
                if rooms and rooms.isdigit():
                    queryset = queryset.filter(blocks__properties__rooms=int(rooms)).distinct()

                min_floor = request.query_params.get('min_floor')
                max_floor = request.query_params.get('max_floor')
                
                if min_floor and min_floor.isdigit():
                    queryset = queryset.filter(blocks__properties__floor__gte=int(min_floor)).distinct()
                if max_floor and max_floor.isdigit():
                    queryset = queryset.filter(blocks__properties__floor__lte=int(max_floor)).distinct()

            min_area = request.query_params.get('min_area')
            max_area = request.query_params.get('max_area')
            
            if min_area and min_area.replace('.', '', 1).isdigit():
                queryset = queryset.filter(blocks__properties__area__gte=float(min_area)).distinct()
            if max_area and max_area.replace('.', '', 1).isdigit():
                queryset = queryset.filter(blocks__properties__area__lte=float(max_area)).distinct()

            min_total_price = request.query_params.get('min_total_price')
            max_total_price = request.query_params.get('max_total_price')
            
            if min_total_price and min_total_price.replace('.', '', 1).isdigit():
                queryset = queryset.filter(blocks__properties__price__gte=float(min_total_price)).distinct()
            if max_total_price and max_total_price.replace('.', '', 1).isdigit():
                queryset = queryset.filter(blocks__properties__price__lte=float(max_total_price)).distinct()
        
        metadata = self.get_filter_metadata(request)
        
        serializer = ResidentialComplexListSerializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'metadata': metadata
        })
    
    @extend_schema(
        request=ResidentialComplexCreateUpdateSerializer,
        responses={status.HTTP_201_CREATED: ResidentialComplexDetailSerializer}
    )
    def post(self, request):
        serializer = ResidentialComplexCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            complex = serializer.save()
            return Response(
                ResidentialComplexDetailSerializer(complex).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_filter_metadata(self, request):
        property_category = request.query_params.get('property_category')
        
        if not property_category:
            return {}
            
        base_qs = Property.objects.filter(category=property_category)
        
        district_id = request.query_params.get('district')
        if district_id and district_id.isdigit():
            base_qs = base_qs.filter(block__complex__district_id=int(district_id))
        
        metadata = {
            'price_range': base_qs.aggregate(
                min_price=Min('price'),
                max_price=Max('price')
            ),
            'area_range': base_qs.aggregate(
                min_area=Min('area'),
                max_area=Max('area')
            )
        }
        
        if property_category == 'APARTMENT':
            metadata.update({
                'floor_range': base_qs.aggregate(
                    min_floor=Min('floor'),
                    max_floor=Max('floor')
                ),
                'rooms_available': list(base_qs.values_list('rooms', flat=True).distinct().order_by('rooms'))
            })
            
        return metadata


class ResidentialComplexDetailView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get_object(self, pk):
        return get_object_or_404(
            ResidentialComplex.objects.prefetch_related(
                'residential_complex_photos', 'blocks', 'blocks__properties', 'district'
            ), 
            pk=pk
        )
    
    def get(self, request, pk):
        complex = self.get_object(pk)
        serializer = ResidentialComplexDetailSerializer(complex)
        return Response(serializer.data)
    
    def put(self, request, pk):
        complex = self.get_object(pk)
        serializer = ResidentialComplexCreateUpdateSerializer(complex, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(ResidentialComplexDetailSerializer(complex).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        complex = self.get_object(pk)
        serializer = ResidentialComplexCreateUpdateSerializer(complex, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ResidentialComplexDetailSerializer(complex).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        complex = self.get_object(pk)
        complex.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResidentialComplexPhotoUploadView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        request=ResidentialComplexPhotoCreateSerializer,
        responses={status.HTTP_201_CREATED: ResidentialComplexPhotoCreateSerializer},
        description="Upload a photo for a residential complex. Requires a multipart/form-data request with a 'photo' field containing the image file."
    )
    def post(self, request, pk):
        complex = get_object_or_404(ResidentialComplex, pk=pk)
        serializer = ResidentialComplexPhotoCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(complex=complex)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResidentialComplexPhotoListView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get(self, request, pk):
        photos = ResidentialComplexPhotos.objects.filter(complex_id=pk)
        serializer = ResidentialComplexPhotosSerializer(photos, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=ResidentialComplexPhotosSerializer,
        responses={status.HTTP_201_CREATED: ResidentialComplexPhotosSerializer},
        description="Create a new photo record for a residential complex. Note that this endpoint expects a URL in the photo_link field, not an actual file upload. For file uploads, use the residential-complexes/{id}/upload-photo/ endpoint."
    )
    def post(self, request, pk):
        complex = get_object_or_404(ResidentialComplex, pk=pk)
        serializer = ResidentialComplexPhotosSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(complex=complex)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResidentialComplexPhotoDetailView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get_object(self, photo_id, complex_id):
        return get_object_or_404(ResidentialComplexPhotos, id=photo_id, complex_id=complex_id)
    
    def get(self, request, pk, photo_id):
        photo = self.get_object(photo_id, pk)
        serializer = ResidentialComplexPhotosSerializer(photo)
        return Response(serializer.data)
    
    def put(self, request, pk, photo_id):
        photo = self.get_object(photo_id, pk)
        serializer = ResidentialComplexPhotosSerializer(photo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, photo_id):
        photo = self.get_object(photo_id, pk)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Block views
class BlockListView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="complex_id", description="Filter by residential complex ID", type=OpenApiTypes.INT, required=False),
        ]
    )
    def get(self, request):
        queryset = Block.objects.all()
        
        complex_id = request.query_params.get('complex_id')
        if complex_id and complex_id.isdigit():
            queryset = queryset.filter(complex_id=int(complex_id))
            
        serializer = BlockSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=BlockSerializer,
        responses={status.HTTP_201_CREATED: BlockSerializer},
        description="Create a new block. The 'complex_id' field is required in the request body."
    )
    def post(self, request):
        serializer = BlockSerializer(data=request.data)
        if serializer.is_valid():
            # Get complex from the validated complex_id
            complex_id = serializer.validated_data.pop('complex_id')
            complex = get_object_or_404(ResidentialComplex, pk=complex_id)
            serializer.save(complex=complex)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlockDetailView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get_object(self, pk):
        return get_object_or_404(Block, pk=pk)
    
    def get(self, request, pk):
        block = self.get_object(pk)
        serializer = BlockSerializer(block)
        return Response(serializer.data)
    
    def put(self, request, pk):
        block = self.get_object(pk)
        serializer = BlockSerializer(block, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        block = self.get_object(pk)
        serializer = BlockSerializer(block, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        block = self.get_object(pk)
        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Property views
class PropertyListView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="block_id", description="Filter by block ID", type=OpenApiTypes.INT, required=False),
            OpenApiParameter(name="complex_id", description="Filter by residential complex ID", type=OpenApiTypes.INT, required=False),
            OpenApiParameter(name="category", description="Filter by property category (APARTMENT, PARKING, BOXROOM, COMMERCE)", type=str, enum=["APARTMENT", "PARKING", "BOXROOM", "COMMERCE"], required=False),
            OpenApiParameter(name="min_price", description="Filter by minimum price", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="max_price", description="Filter by maximum price", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="min_area", description="Filter by minimum area", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="max_area", description="Filter by maximum area", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="rooms", description="Filter by number of rooms (for APARTMENT category)", type=OpenApiTypes.INT, required=False),
        ]
    )
    def get(self, request):
        queryset = Property.objects.all().prefetch_related('property_photos', 'property_videos', 'block', 'block__complex')
        
        block_id = request.query_params.get('block_id')
        if block_id and block_id.isdigit():
            queryset = queryset.filter(block_id=int(block_id))
            
        complex_id = request.query_params.get('complex_id')
        if complex_id and complex_id.isdigit():
            queryset = queryset.filter(block__complex_id=int(complex_id))
            
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price and min_price.replace('.', '', 1).isdigit():
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price and max_price.replace('.', '', 1).isdigit():
            queryset = queryset.filter(price__lte=float(max_price))
            
        min_area = request.query_params.get('min_area')
        max_area = request.query_params.get('max_area')
        if min_area and min_area.replace('.', '', 1).isdigit():
            queryset = queryset.filter(area__gte=float(min_area))
        if max_area and max_area.replace('.', '', 1).isdigit():
            queryset = queryset.filter(area__lte=float(max_area))
            
        rooms = request.query_params.get('rooms')
        if rooms and rooms.isdigit():
            queryset = queryset.filter(rooms=int(rooms))
            
        serializer = PropertySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=PropertySerializer,
        responses={status.HTTP_201_CREATED: PropertySerializer},
        description="Create a new property. The 'block_id' field is required in the request body. Note that the price field is automatically calculated as area * price_per_sqm."
    )
    def post(self, request):
        serializer = PropertySerializer(data=request.data)
        if serializer.is_valid():
            block_id = serializer.validated_data.pop('block_id')
            block = get_object_or_404(Block, pk=block_id)
            serializer.save(block=block)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyDetailView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get_object(self, pk):
        return get_object_or_404(
            Property.objects.prefetch_related('property_photos', 'property_videos', 'block', 'block__complex'),
            pk=pk
        )
    
    def get(self, request, pk):
        property = self.get_object(pk)
        serializer = PropertyDetailSerializer(property)
        return Response(serializer.data)
    
    def put(self, request, pk):
        property = self.get_object(pk)
        serializer = PropertySerializer(property, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        property = self.get_object(pk)
        serializer = PropertySerializer(property, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        property = self.get_object(pk)
        property.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Property Photos views
class PropertyPhotoListView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request, property_id):
        photos = PropertyPhotos.objects.filter(property_id=property_id)
        serializer = PropertyPhotosSerializer(photos, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=PropertyPhotoCreateSerializer,
        responses={status.HTTP_201_CREATED: PropertyPhotoCreateSerializer},
        description="Upload a photo for a property. Requires a multipart/form-data request with a 'photo' field containing the image file."
    )
    def post(self, request, property_id):
        property = get_object_or_404(Property, pk=property_id)
        serializer = PropertyPhotoCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(property=property)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyPhotoDetailView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get_object(self, photo_id, property_id):
        return get_object_or_404(PropertyPhotos, id=photo_id, property_id=property_id)
    
    def get(self, request, property_id, photo_id):
        photo = self.get_object(photo_id, property_id)
        serializer = PropertyPhotosSerializer(photo)
        return Response(serializer.data)
    
    def delete(self, request, property_id, photo_id):
        photo = self.get_object(photo_id, property_id)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Property Videos views
class PropertyVideoListView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get(self, request, property_id):
        videos = PropertyVideos.objects.filter(property_id=property_id)
        serializer = PropertyVideosSerializer(videos, many=True)
        return Response(serializer.data)
    
    def post(self, request, property_id):
        property = get_object_or_404(Property, pk=property_id)
        serializer = PropertyVideosSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(property=property)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyVideoDetailView(APIView):
    permission_classes = [ReadOnlyForAnyone]
    
    def get_object(self, video_id, property_id):
        return get_object_or_404(PropertyVideos, id=video_id, property_id=property_id)
    
    def get(self, request, property_id, video_id):
        video = self.get_object(video_id, property_id)
        serializer = PropertyVideosSerializer(video)
        return Response(serializer.data)
    
    def put(self, request, property_id, video_id):
        video = self.get_object(video_id, property_id)
        serializer = PropertyVideosSerializer(video, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, property_id, video_id):
        video = self.get_object(video_id, property_id)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
