from django import forms
from .models import Property, ResidentialComplex, ResidentialComplexPhotos, PropertyPhotos, PropertyVideos
from .fields import S3FileField, S3ImageField, S3VideoField


class PropertyAdminForm(forms.ModelForm):
    layout_file = S3ImageField(
        required=False, 
        label='Layout (file)',
        help_text='Upload layout file. Available extensions: JPG, JPEG, PNG, GIF, WEBP. Will be saved on S3.',
        s3_path='property_layouts'
    )
    
    class Meta:
        model = Property
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.layout:
            self.fields['layout_file'].initial = self.instance.layout
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if 'layout_file' in self.cleaned_data and self.cleaned_data['layout_file']:
            instance.layout = self.cleaned_data['layout_file']
        
        if commit:
            instance.save()
        
        return instance


class PropertyPhotoAdminForm(forms.ModelForm):
    photo = S3ImageField(
        required=False,
        label='Фото',
        help_text='Загрузите фото объекта недвижимости. Поддерживаемые форматы: JPG, JPEG, PNG, GIF, WEBP. Будет сохранено на S3.',
        s3_path='property_photos'
    )
    
    class Meta:
        model = PropertyPhotos
        fields = ['property', 'photo']
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Save the uploaded photo URL to the photo_link field
        if 'photo' in self.cleaned_data and self.cleaned_data['photo']:
            instance.photo_link = self.cleaned_data['photo']
        
        if commit:
            instance.save()
        
        return instance


class PropertyVideoAdminForm(forms.ModelForm):
    video = S3VideoField(
        required=False,
        label='Видео',
        help_text='Загрузите видео объекта недвижимости. Поддерживаемые форматы: MP4, MOV, AVI, WEBM. Будет сохранено на S3.',
        s3_path='property_videos'
    )
    
    class Meta:
        model = PropertyVideos
        fields = ['property', 'video']
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Save the uploaded video URL to the video_link field
        if 'video' in self.cleaned_data and self.cleaned_data['video']:
            instance.video_link = self.cleaned_data['video']
        
        if commit:
            instance.save()
        
        return instance


class ResidentialComplexPhotoAdminForm(forms.ModelForm):
    photo = S3ImageField(
        required=True,
        label='Photo',
        help_text='Upload photo of the residential ccomlex. Available extensions: JPG, JPEG, PNG, GIF, WEBP. Will be saved on S3.',
        s3_path='residential_complex_photos'
    )
    
    class Meta:
        model = ResidentialComplexPhotos
        fields = ['complex', 'photo']
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if 'photo' in self.cleaned_data and self.cleaned_data['photo']:
            instance.photo_link = self.cleaned_data['photo']
        
        if commit:
            instance.save()
        
        return instance 