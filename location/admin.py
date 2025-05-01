from django.contrib import admin
from .models import City, District

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display  = ('name', 'city', 'description')
    list_filter   = ('city',)
    search_fields = ('name',)
