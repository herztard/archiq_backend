from django import forms
from clients.s3 import S3Client, generate_unique_filename
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .widgets import S3FileUploadWidget


class S3FileField(forms.FileField):
    widget = S3FileUploadWidget
    
    def __init__(self, *args, **kwargs):
        self.s3_path = kwargs.pop('s3_path', 'uploads')
        self.allowed_extensions = kwargs.pop('allowed_extensions', None)
        
        if self.allowed_extensions:
            self.file_extension_validator = FileExtensionValidator(allowed_extensions=self.allowed_extensions)
            kwargs['validators'] = kwargs.get('validators', [])
        
        super().__init__(*args, **kwargs)
    
    def to_python(self, data):
        if data is None or isinstance(data, str):
            return data
        
        file = super().to_python(data)
        if file is None:
            return None
        
        if hasattr(self, 'file_extension_validator'):
            self.file_extension_validator(file)
        
        unique_name = generate_unique_filename(file.name)
        destination = f"{self.s3_path}/{unique_name}"
        
        s3 = S3Client()
        file.seek(0)
        s3.upload_to_s3(file_content=file.read(), destination_blob_name=destination)
        
        return f"{settings.AWS_S3_FULL_URL}/{destination}"
    
    def prepare_value(self, value):
        return value


class S3ImageField(S3FileField):
    default_validators = []
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('allowed_extensions', ['jpg', 'jpeg', 'png', 'gif', 'webp'])
        super().__init__(*args, **kwargs)
        
        
class S3VideoField(S3FileField):
    default_validators = []
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('allowed_extensions', ['mp4', 'mov', 'avi', 'webm'])
        super().__init__(*args, **kwargs) 