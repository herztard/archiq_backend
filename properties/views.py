from django.db.models import Min, Max, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.exceptions import NotFound

from .models import ResidentialComplex, Block, Property, ResidentialComplexPhotos, PropertyPhotos, PropertyVideos
from sales.models import PropertyPurchase
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

        property_category = request.query_params.get('property_category', 'APARTMENT')
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
        available_properties = Property.objects.exclude(
            property_purchases__status__in=['RESERVED', 'PAID', 'COMPLETED']
        )
        
        property_category = request.query_params.get('property_category', 'APARTMENT')
        if property_category:
            available_properties = available_properties.filter(category=property_category)
            
            if property_category == 'APARTMENT':
                class_type = request.query_params.get('class_type')
                if class_type:
                    available_properties = available_properties.filter(block__complex__class_type=class_type)
                
                rooms = request.query_params.get('rooms')
                if rooms and rooms.isdigit():
                    available_properties = available_properties.filter(rooms=int(rooms))
        
        district_id = request.query_params.get('district')
        if district_id and district_id.isdigit():
            available_properties = available_properties.filter(block__complex__district_id=int(district_id))
        
        min_floor = request.query_params.get('min_floor')
        max_floor = request.query_params.get('max_floor')
        if min_floor and min_floor.isdigit():
            available_properties = available_properties.filter(floor__gte=int(min_floor))
        if max_floor and max_floor.isdigit():
            available_properties = available_properties.filter(floor__lte=int(max_floor))
        
        min_area = request.query_params.get('min_area')
        max_area = request.query_params.get('max_area')
        if min_area and min_area.replace('.', '', 1).isdigit():
            available_properties = available_properties.filter(area__gte=float(min_area))
        if max_area and max_area.replace('.', '', 1).isdigit():
            available_properties = available_properties.filter(area__lte=float(max_area))
        
        min_total_price = request.query_params.get('min_total_price')
        max_total_price = request.query_params.get('max_total_price')
        if min_total_price and min_total_price.replace('.', '', 1).isdigit():
            available_properties = available_properties.filter(price__gte=float(min_total_price))
        if max_total_price and max_total_price.replace('.', '', 1).isdigit():
            available_properties = available_properties.filter(price__lte=float(max_total_price))
            
        metadata = {
            'min_total_price': available_properties.aggregate(Min('price'))['price__min'],
            'max_total_price': available_properties.aggregate(Max('price'))['price__max'],
            'min_price_per_sqm': available_properties.aggregate(Min('price_per_sqm'))['price_per_sqm__min'],
            'max_price_per_sqm': available_properties.aggregate(Max('price_per_sqm'))['price_per_sqm__max'],
            'min_area': available_properties.aggregate(Min('area'))['area__min'],
            'max_area': available_properties.aggregate(Max('area'))['area__max'],
            'min_floor': available_properties.aggregate(Min('floor'))['floor__min'],
            'max_floor': available_properties.aggregate(Max('floor'))['floor__max'],
            'available_properties_count': available_properties.count()
        }
        
        if property_category == 'APARTMENT':
            metadata.update({
                'rooms_available': list(available_properties.values_list('rooms', flat=True).distinct().order_by('rooms'))
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
            OpenApiParameter(name="complex_id", description="Filter by residential complex ID", type=OpenApiTypes.INT, required=False),
            OpenApiParameter(name="category", description="Filter by property category (APARTMENT, PARKING, BOXROOM, COMMERCE)", type=str, enum=["APARTMENT", "PARKING", "BOXROOM", "COMMERCE"], required=False),
            OpenApiParameter(name="class_type", description="Filter by class type (for APARTMENT category)", type=str, enum=["STANDARD", "COMFORT", "BUSINESS", "PREMIUM"], required=False),
            OpenApiParameter(name="min_price", description="Filter by minimum price", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="max_price", description="Filter by maximum price", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="min_area", description="Filter by minimum area", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="max_area", description="Filter by maximum area", type=OpenApiTypes.NUMBER, required=False),
            OpenApiParameter(name="rooms", description="Filter by number of rooms (for APARTMENT category)", type=OpenApiTypes.INT, required=False),
        ],
        description="List available properties. Properties with RESERVED, PAID, or COMPLETED status are not included in the results."
    )
    def get(self, request):
        queryset = Property.objects.all().prefetch_related('property_photos', 'property_videos', 'block', 'block__complex')
        
        queryset = queryset.exclude(
            property_purchases__status__in=['PAID', 'RESERVED', 'COMPLETED']
        )
            
        complex_id = request.query_params.get('complex_id')
        if complex_id and complex_id.isdigit():
            queryset = queryset.filter(block__complex_id=int(complex_id))
            
        category = request.query_params.get('category', 'APARTMENT')
        if category:
            queryset = queryset.filter(category=category)
            
            if category == 'APARTMENT':
                class_type = request.query_params.get('class_type')
                if class_type:
                    queryset = queryset.filter(block__complex__class_type=class_type)
            
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
            
        metadata = self.get_filter_metadata(request, queryset)
        
        serializer = PropertySerializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'metadata': metadata
        })
    
    def get_filter_metadata(self, request, filtered_properties):
        metadata = {}
        
        metadata.update({
            'min_total_price': filtered_properties.aggregate(Min('price'))['price__min'],
            'max_total_price': filtered_properties.aggregate(Max('price'))['price__max'],
            'min_price_per_sqm': filtered_properties.aggregate(Min('price_per_sqm'))['price_per_sqm__min'],
            'max_price_per_sqm': filtered_properties.aggregate(Max('price_per_sqm'))['price_per_sqm__max'],
            'min_area': filtered_properties.aggregate(Min('area'))['area__min'],
            'max_area': filtered_properties.aggregate(Max('area'))['area__max'],
            'min_floor': filtered_properties.aggregate(Min('floor'))['floor__min'],
            'max_floor': filtered_properties.aggregate(Max('floor'))['floor__max'],
            'available_properties_count': filtered_properties.count()
        })
        
        available_complex_ids = filtered_properties.values_list('block__complex_id', flat=True).distinct()
        available_complexes = ResidentialComplex.objects.filter(id__in=available_complex_ids)
        
        metadata['available_residential_complexes'] = ResidentialComplexListSerializer(
            available_complexes, 
            many=True
        ).data
        
        # Category-specific metadata
        category = request.query_params.get('category', 'APARTMENT')
        if category == 'APARTMENT':
            metadata.update({
                'rooms_available': list(filtered_properties.values_list('rooms', flat=True).distinct().order_by('rooms'))
            })
            
        return metadata
    
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
        property = get_object_or_404(
            Property.objects.prefetch_related('property_photos', 'property_videos', 'block', 'block__complex'),
            pk=pk
        )
        
        if property.property_purchases.filter(status__in=['PAID', 'RESERVED', 'COMPLETED']).exists():
            raise NotFound("Property is not available")
            
        return property
    
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
