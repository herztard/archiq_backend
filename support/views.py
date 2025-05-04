from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Report, ReportAttachment
from .serializers import (
    ReportRetrieveSerializer, 
    ReportCreateSerializer,
)
from properties.models import Property


class IsOwnerPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
            
        if request.method == 'POST':
            property_id = request.data.get('property')
            if not property_id:
                return False
                
            try:
                property_obj = Property.objects.get(pk=property_id)
                return property_obj.property_purchases.filter(
                    user=request.user,
                    status='COMPLETED'
                ).exists()
            except Property.DoesNotExist:
                return False
                
        return True

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class ReportListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        description="List all reports created by the authenticated user",
        responses={status.HTTP_200_OK: ReportRetrieveSerializer(many=True)}
    )
    def get(self, request):
        reports = Report.objects.filter(user=request.user).prefetch_related('attachments')
        serializer = ReportRetrieveSerializer(reports, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Create a new report for a property owned by the authenticated user, with optional file attachments",
        request=ReportCreateSerializer,
        responses={status.HTTP_201_CREATED: ReportRetrieveSerializer}
    )
    def post(self, request):
        serializer = ReportCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            report = serializer.save(user=request.user)
            return Response(
                ReportRetrieveSerializer(report).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportDetailView(APIView):
    permission_classes = [IsOwnerPermission]
    
    def get_object(self, pk, user):
        return get_object_or_404(Report, pk=pk, user=user)
    
    @extend_schema(
        description="Retrieve details of a specific report",
        responses={status.HTTP_200_OK: ReportRetrieveSerializer}
    )
    def get(self, request, pk):
        report = self.get_object(pk, request.user)
        serializer = ReportRetrieveSerializer(report)
        return Response(serializer.data)

    @extend_schema(
        description="Delete a report (only if it's in NEW status)",
        responses={status.HTTP_204_NO_CONTENT: None}
    )
    def delete(self, request, pk):
        report = self.get_object(pk, request.user)
        
        if report.status != 'NEW':
            return Response(
                {"detail": "Only NEW reports can be deleted"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

