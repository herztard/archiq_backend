from django.db import models

from archiq_backend import settings
from properties.models import Property


# Create your models here.
class Report(models.Model):
    STATUS_CHOICES = (
        ("NEW", "Новая"),
        ("IN PROGRESS", "В процессе"),
        ("CANCELED", "Отменена"),
        ("RESOLVED", "Решена"),
        ("UNRESOLVABLE", "Невозможно решить"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default=STATUS_CHOICES[0][0])
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report #{self.id} by {self.user}"

    class Meta:
        db_table = "reports"


class ReportAttachment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='attachments')
    file_link = models.URLField()

    def __str__(self):
        return f"Attachment {self.file_link} for report #{self.report.id}"

    class Meta:
        db_table = "report_attachments"


