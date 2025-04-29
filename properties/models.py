from django.db import models

from location.models import District


# Create your models here.
class ResidentialComplex(models.Model):
    CLASS_TYPE_CHOICES = (
        ("STANDARD", "Стандарт"),
        ("COMFORT", 'Комфорт'),
        ("BUSINESS", 'Бизнес'),
        ("PREMIUM", "Премиум")
    )

    HEATING_TYPE_CHOICES = (
        ("GAS", "Газовое"),
        ("ELECTRIC", "Электрическое"),
        ("CENTRAL", "Центральное")
    )

    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="residential_complexes")
    name = models.CharField(max_length=255)
    address = models.TextField()
    class_type = models.CharField(choices=CLASS_TYPE_CHOICES, max_length=255)
    construction_technology = models.CharField(max_length=100)
    heating_type = models.CharField(max_length=255, choices=HEATING_TYPE_CHOICES)
    has_elevator_pass = models.BooleanField(default=False)
    has_elevator_cargo = models.BooleanField(default=False)
    ceiling_height = models.DecimalField(max_digits=5, decimal_places=2)
    block_number = models.IntegerField()
    down_payment = models.DecimalField(max_digits=10, decimal_places=2)
    installment_plan = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    link_on_map = models.URLField()
    description_full = models.TextField()
    description_short = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "residential_complexes"

class Block(models.Model):
    BUILDING_STATUS_CHOICES = (
        ("EXСAVATION", "На стадии котлована"),
        ("UNDER CONSTRUCTION", "Строится"),
        ("COMPLETED", "Постройка завершена")
    )

    complex = models.ForeignKey(ResidentialComplex, on_delete=models.CASCADE, related_name="blocks")
    block_number = models.IntegerField(null=True, blank=True, default=1)
    entrance_number = models.IntegerField(null=True, blank=True, default=1)
    total_floors = models.IntegerField()
    queue = models.IntegerField(null=True, blank=True, default=1)
    deadline_year = models.IntegerField(null=True, blank=True)
    deadline_querter = models.IntegerField(null=True, blank=True)
    total_apartments = models.IntegerField(null=True, blank=True)
    building_status = models.CharField(max_length=255, choices=BUILDING_STATUS_CHOICES, default=BUILDING_STATUS_CHOICES[0][0])
    link_on_map = models.URLField()

    def __str__(self):
        return f"{self.complex.name}, к{self.block_number}"

    class Meta:
        db_table = "blocks"


class Category(models.Model):
    CATEGORY_TYPE_CHOICES = (
        ("APARTMENT", "Apartment"),
        ("PARKING", "Parking"),
        ("BOXROOM", "Boxroom"),
        ("COMMERCE", "Commerce"),
    )

    name = models.CharField(max_length=50, choices=CATEGORY_TYPE_CHOICES)
    def __str__(self):
        return self.name

    class Meta:
        db_table = "property_categories"


class Property(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="properties")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="properties")
    number = models.IntegerField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    floor = models.IntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.IntegerField(null=True, blank=True)
    renovation_type = models.CharField(max_length=50, null=True, blank=True)
    wall_material = models.CharField(max_length=50, null=True, blank=True)
    layout = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    entrance = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.category.name} #{self.number} в {self.block.complex.name}, к{self.block.block_number}"

    class Meta:
        db_table = "properties"

class PropertyPhotos(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_photos")
    photo_link = models.URLField()

    def __str__(self):
        return f"Photo {self.photo_link} for {self.property}"

    class Meta:
        db_table = "property_photos"

class PropertyVideos(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_videos")
    video_link = models.URLField()

    class Meta:
        db_table = "property_videos"

    def __str__(self):
        return f"Video {self.video_link} for {self.property}"