from rest_framework import serializers
from rest_framework import status
from .models import Report, ReportAttachment
from users.serializers import ProfileSerializer


class ReportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAttachment
        fields = ['id', 'file_link']


class ReportAttachmentCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_link = serializers.URLField(read_only=True)

    class Meta:
        model = ReportAttachment
        fields = ['file', 'file_link']

    def create(self, validated_data):
        file = validated_data.pop('file')
        report = validated_data.get('report')

        # Generate a unique filename
        from clients.s3 import S3Client, generate_unique_filename
        from django.conf import settings

        unique_name = generate_unique_filename(file.name)
        destination = f"report_attachments/{unique_name}"

        s3 = S3Client()
        file.seek(0)
        s3.upload_to_s3(file_content=file.read(), destination_blob_name=destination)

        file_link = f"{settings.AWS_S3_FULL_URL}/{destination}"

        return ReportAttachment.objects.create(
            report=report,
            file_link=file_link
        )


class ReportRetrieveSerializer(serializers.ModelSerializer):

    user = ProfileSerializer(read_only=True)
    attachments = ReportAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'user', 'property', 'title', 'content', 
            'status', 'created_at', 'updated_at', 
            'resolved_at', 'attachments'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'resolved_at']


class ReportCreateSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    attachments = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Report
        fields = [
            'id', 'user', 'property', 'title', 'content', 
            'created_at', 'updated_at',
            'resolved_at', 'attachments'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'resolved_at']
        
    def validate(self, data):
        property_obj = data.get('property')
        user = self.context['request'].user
        
        if not property_obj.property_purchases.filter(
            user=user, 
            status='COMPLETED'
        ).exists():
            raise serializers.ValidationError("You can only report issues for properties you own")
        
        return data
    
    def create(self, validated_data):
        attachments_data = validated_data.pop('attachments', [])
        
        report = Report.objects.create(**validated_data)
        
        for attachment_file in attachments_data:
            from clients.s3 import S3Client, generate_unique_filename
            from django.conf import settings
            
            unique_name = generate_unique_filename(attachment_file.name)
            destination = f"report_attachments/{unique_name}"
            
            s3 = S3Client()
            attachment_file.seek(0)
            s3.upload_to_s3(
                file_content=attachment_file.read(), 
                destination_blob_name=destination
            )
            
            file_link = f"{settings.AWS_S3_FULL_URL}/{destination}"
            ReportAttachment.objects.create(
                report=report,
                file_link=file_link
            )
        
        return report


