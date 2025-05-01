from django.db import models

from archiq_backend import settings
from properties.models import Property


# Create your models here.
class PropertyPurchase(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("RESERVED", "Reserved"),
        ("PAID", "Paid"),
        ("CANCELED", "Canceled"),
        ("COMPLETED", "Completed"),
    )

    PURPOSE_CHOICES = (
        ("BUYING", "Buying"),
        ("RENTING", "Renting"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='property_purchases')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_purchases')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    purchase_purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, default=PURPOSE_CHOICES[0][0])

    def __str__(self):
        return f"{self.user} purchases {self.property}"

    class Meta:
        db_table = "property_purchases"