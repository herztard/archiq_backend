from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_applicant', 'property', 'residential_complex', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone_number', 'user__first_name', 'user__last_name', 'user__phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Applicant Information', {
            'fields': ('user', 'name', 'phone_number')
        }),
        ('Property Interest', {
            'fields': ('property', 'residential_complex')
        }),
        ('Application Details', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )
    
    def get_applicant(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.phone_number})"
        return f"{obj.name} ({obj.phone_number})"
    get_applicant.short_description = 'Applicant'
