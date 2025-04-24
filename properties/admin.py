from django.contrib import admin
from .models import ResidentialComplex, Block, Category, Property, PropertyPhotos, PropertyVideos

class BlockInline(admin.TabularInline):
    model = Block
    extra = 0

@admin.register(ResidentialComplex)
class ResidentialComplexAdmin(admin.ModelAdmin):
    inlines      = [BlockInline]
    list_display = ('name', 'district', 'class_type', 'heating_type', 'created_at')
    list_filter  = ('class_type', 'heating_type', 'district')
    search_fields= ('name', 'address')
    raw_id_fields= ('district',)

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('complex', 'block_number', 'entrance_number', 'building_status', 'deadline_year', 'deadline_querter')
    list_filter  = ('building_status', 'deadline_year')
    raw_id_fields= ('complex',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class PropertyPhotosInline(admin.TabularInline):
    model = PropertyPhotos
    extra = 0

class PropertyVideosInline(admin.TabularInline):
    model = PropertyVideos
    extra = 0

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines      = [PropertyPhotosInline, PropertyVideosInline]
    list_display = ('id', 'category', 'number', 'block', 'price', 'area', 'floor')
    list_filter  = ('category', 'floor', 'block__complex')
    search_fields= ('number', 'description')
    raw_id_fields= ('block', 'category')
