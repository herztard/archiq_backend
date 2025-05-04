from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

from .models import Application
from .serializers import (
    AuthenticatedApplicationSerializer,
    UnauthenticatedApplicationSerializer,
    ApplicationListSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    post=extend_schema(
        summary="Create a new application",
        description="Submit an application with user details and property interest. Works for both authenticated and anonymous users.",
        request=UnauthenticatedApplicationSerializer,
        responses={201: dict, 400: dict},
        examples=[
            OpenApiExample(
                'Unauthenticated example',
                value={
                    'name': 'John Doe',
                    'phone_number': '+77771234567'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Authenticated example',
                value={},
                request_only=True,
            ),
            OpenApiExample(
                'With property example',
                value={
                    'name': 'John Doe',
                    'phone_number': '+77771234567',
                    'property': 1
                },
                request_only=True,
            ),
            OpenApiExample(
                'With residential complex example',
                value={
                    'name': 'John Doe',
                    'phone_number': '+77771234567',
                    'residential_complex': 1
                },
                request_only=True,
            ),
            OpenApiExample(
                'Success response',
                value={
                    'id': 1,
                    'message': 'Application submitted successfully'
                },
                response_only=True,
            ),
            OpenApiExample(
                'Error response',
                value={
                    'phone_number': ['Enter a valid phone number.']
                },
                response_only=True,
            )
        ]
    )
)
class ApplicationCreateView(generics.CreateAPIView):
    """
    API view for creating applications. Handles both authenticated and unauthenticated users.
    
    For authenticated users: Uses token authentication and links to existing user.
    For unauthenticated users: Requires name and phone_number.
    
    Both cases can optionally include property or residential_complex IDs.
    """
    permission_classes = [AllowAny]
    serializer_class = UnauthenticatedApplicationSerializer
    
    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return AuthenticatedApplicationSerializer
        return UnauthenticatedApplicationSerializer
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Handle authenticated user
            serializer = AuthenticatedApplicationSerializer(
                data=request.data,
                context={'request': request}
            )
        else:
            # Handle unauthenticated user
            serializer = UnauthenticatedApplicationSerializer(data=request.data)
        
        if serializer.is_valid():
            application = serializer.save()
            return Response(
                {
                    'id': application.id,
                    'message': 'Application submitted successfully'
                }, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="List all applications",
        description="Admin only: List all submitted applications with optional status filtering.",
        responses={200: ApplicationListSerializer(many=True)}
    )
)
class ApplicationListView(generics.ListAPIView):
    """
    API view for listing applications.
    Only accessible by staff/admin users.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination
    serializer_class = ApplicationListSerializer
    queryset = Application.objects.all()
    
    def get(self, request, *args, **kwargs):
        applications = self.get_queryset()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_applications = paginator.paginate_queryset(applications, request)
        
        serializer = self.get_serializer(paginated_applications, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Get application details",
        description="Admin only: Retrieve details for a specific application.",
        responses={200: ApplicationListSerializer, 404: dict}
    ),
    patch=extend_schema(
        summary="Update application",
        description="Admin only: Update application details, such as status.",
        request=ApplicationListSerializer,
        responses={200: ApplicationListSerializer, 400: dict, 404: dict},
        examples=[
            OpenApiExample(
                'Update status example',
                value={
                    'status': 'CONTACTED'
                },
                request_only=True,
            ),
        ]
    ),
    delete=extend_schema(
        summary="Delete application",
        description="Admin only: Delete an application.",
        responses={204: None, 404: dict}
    )
)
class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting applications.
    Only accessible by staff/admin users.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ApplicationListSerializer
    queryset = Application.objects.all()
    lookup_field = 'pk'
    
    def get_object(self):
        try:
            return Application.objects.get(pk=self.kwargs['pk'])
        except Application.DoesNotExist:
            return None
    
    def get(self, request, *args, **kwargs):
        application = self.get_object()
        if not application:
            return Response(
                {'error': 'Application not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):
        application = self.get_object()
        if not application:
            return Response(
                {'error': 'Application not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(
            application, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        application = self.get_object()
        if not application:
            return Response(
                {'error': 'Application not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
