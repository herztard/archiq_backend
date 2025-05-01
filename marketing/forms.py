from django import forms
from .models import Banner
from properties.fields import S3ImageField


class BannerAdminForm(forms.ModelForm):
    image = S3ImageField(
        required=False,
        label='Banner image',
        help_text='Upload banner\' image. Available extentions: JPG, JPEG, PNG, GIF, WEBP. Will be saved on S3.',
        s3_path='banner'
    )
    
    class Meta:
        model = Banner
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.image_link:
            self.fields['image'].initial = self.instance.image_link
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if 'image' in self.cleaned_data and self.cleaned_data['image']:
            instance.image_link = self.cleaned_data['image']
        
        if commit:
            instance.save()
        
        return instance 