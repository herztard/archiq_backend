from django.contrib import admin
from .models import Banner
from .forms import BannerAdminForm

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    form = BannerAdminForm
    list_display = ('title', 'start_at', 'end_at', 'target_url')
    list_filter = ('start_at', 'end_at')
    search_fields = ('title', 'subtitle')
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'target_url', 'start_at', 'end_at')
        }),
        ('Изображение', {
            'fields': ('image_link', 'image'),
            'description': 'Загрузите новое изображение или используйте существующую ссылку.'
        }),
    )
