from django.contrib import admin
from .models import Report, ReportAttachment

class ReportAttachmentInline(admin.TabularInline):
    model = ReportAttachment
    extra = 0

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    inlines = [ReportAttachmentInline]
    list_display = ('id', 'user', 'property', 'title', 'status', 'created_at', 'updated_at', 'resolved_at')
    list_filter  = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'resolution_notes')
    raw_id_fields = ('user', 'property')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')
    ordering = ('-created_at',)

@admin.register(ReportAttachment)
class ReportAttachmentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'report', 'file_link')
    search_fields = ('file_link',)
    raw_id_fields  = ('report',)
