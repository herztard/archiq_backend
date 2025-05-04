from django.contrib import admin
from .models import ResidentialComplex, Block, Property, PropertyPhotos, PropertyVideos, ResidentialComplexPhotos
from .forms import PropertyAdminForm, PropertyPhotoAdminForm, ResidentialComplexPhotoAdminForm, PropertyVideoAdminForm


class BlockInline(admin.TabularInline):
    model = Block
    extra = 0


class ResidentialComplexPhotosInline(admin.TabularInline):
    model = ResidentialComplexPhotos
    extra = 0
    form = ResidentialComplexPhotoAdminForm
    fields = ['complex', 'photo']


@admin.register(ResidentialComplexPhotos)
class ResidentialComplexPhotosAdmin(admin.ModelAdmin):
    form = ResidentialComplexPhotoAdminForm
    list_display = ('id', 'complex', 'photo_link')
    search_fields = ('complex__name',)


@admin.register(ResidentialComplex)
class ResidentialComplexAdmin(admin.ModelAdmin):
    inlines      = [BlockInline, ResidentialComplexPhotosInline]
    list_display = ('name', 'district', 'class_type', 'heating_type', 'created_at')
    list_filter  = ('class_type', 'heating_type', 'district')
    search_fields= ('name', 'address')


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('complex', 'block_number', 'entrance_number', 'building_status', 'deadline_year', 'deadline_querter')
    list_filter  = ('building_status', 'deadline_year')


class PropertyPhotosInline(admin.TabularInline):
    model = PropertyPhotos
    extra = 0
    form = PropertyPhotoAdminForm
    fields = ['property', 'photo']


class PropertyVideosInline(admin.TabularInline):
    model = PropertyVideos
    extra = 0
    form = PropertyVideoAdminForm
    fields = ['property', 'video']


@admin.register(PropertyPhotos)
class PropertyPhotosAdmin(admin.ModelAdmin):
    form = PropertyPhotoAdminForm
    list_display = ('id', 'property', 'photo_link')
    search_fields = ('property__number',)


@admin.register(PropertyVideos)
class PropertyVideosAdmin(admin.ModelAdmin):
    form = PropertyVideoAdminForm
    list_display = ('id', 'property', 'video_link')
    search_fields = ('property__number',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    form = PropertyAdminForm
    inlines = [PropertyPhotosInline, PropertyVideosInline]
    list_display = ('id', 'category', 'number', 'block', 'price', 'area', 'floor')
    list_filter = ('category', 'floor', 'block__complex')
    search_fields = ('number',)
    fieldsets = (
        (None, {
            'fields': ('block', 'category', 'number', 'price_per_sqm', 'rental_price', 'floor', 
                       'area', 'rooms')
        }),
        ('Дополнительная информация', {
            'fields': ('layout', 'layout_file'),
            'classes': ('collapse',),
        }),
    )

