from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

from properties.models import Property, ResidentialComplex


class Application(models.Model):
    STATUS_CHOICES = (
        ('NEW', 'New'),
        ('PROCESSING', 'Processing'),
        ('CONTACTED', 'Contacted'),
        ('COMPLETED', 'Completed'),
        ('CANCELED', 'Canceled'),
    )

    # User information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='applications'
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True, region='KZ')
    
    # Property interest
    property = models.ForeignKey(
        Property, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='applications'
    )
    residential_complex = models.ForeignKey(
        ResidentialComplex, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='applications'
    )
    
    # Application details
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='NEW'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'applications'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"Application #{self.id} by {self.user}"
        return f"Application #{self.id} by {self.name} ({self.phone_number})"
