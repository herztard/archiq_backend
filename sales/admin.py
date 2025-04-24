from django.contrib import admin
from .models import PropertyPurchase

@admin.register(PropertyPurchase)
class PropertyPurchaseAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'property', 'status', 'purchase_purpose')
    list_filter   = ('status', 'purchase_purpose')
    search_fields = ('user__username', 'property__id')
    raw_id_fields = ('user', 'property')
