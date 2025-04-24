from django.contrib import admin
from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display  = ('title', 'start_at', 'end_at', 'target_url')
    list_filter   = ('start_at', 'end_at')
    search_fields = ('title', 'subtitle')
