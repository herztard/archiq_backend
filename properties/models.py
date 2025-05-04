from django.db import models

from location.models import District


# Create your models here.
class ResidentialComplex(models.Model):
    CLASS_TYPE_CHOICES = (
        ("STANDARD", "Standard"),
        ("COMFORT", 'Comfort'),
        ("BUSINESS", 'Business'),
        ("PREMIUM", "Premium")
    )

    HEATING_TYPE_CHOICES = (
        ("GAS", "Gas heating"),
        ("ELECTRIC", "Electric heating"),
        ("CENTRAL", "Central heating")
    )

    CONSTRUCTION_TECHNOLOGY_CHOICES = (
        ("MONOLITHIC", "Monolithic"),
        ("PRECAST LARGE-PANEL", "Precast large-panel"),
        ("MASONRY", "Masonry"),
    )

    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="residential_complexes")
    name = models.CharField(max_length=255)
    address = models.TextField()
    class_type = models.CharField(choices=CLASS_TYPE_CHOICES, max_length=255)
    construction_technology = models.CharField(max_length=100, choices=CONSTRUCTION_TECHNOLOGY_CHOICES)
    heating_type = models.CharField(max_length=255, choices=HEATING_TYPE_CHOICES)
    has_elevator_pass = models.BooleanField(default=False)
    has_elevator_cargo = models.BooleanField(default=False)
    ceiling_height = models.DecimalField(max_digits=5, decimal_places=2)
    block_number = models.IntegerField()
    down_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    installment_plan = models.CharField(max_length=50, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    link_on_map = models.URLField(null=True)
    description_full = models.TextField(null=True)
    description_short = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "residential_complexes"


class ResidentialComplexPhotos(models.Model):
    complex = models.ForeignKey(ResidentialComplex, on_delete=models.CASCADE, related_name="residential_complex_photos")
    photo_link = models.URLField()

    def __str__(self):
        return f"Photo {self.photo_link} for {self.complex}"

    class Meta:
        db_table = "residential_complex_photos"


class Block(models.Model):
    BUILDING_STATUS_CHOICES = (
        ("EXСAVATION", "At the excavation stage"),
        ("UNDER CONSTRUCTION", "Under construction"),
        ("COMPLETED", "The construction is completed")
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


class Property(models.Model):
    CATEGORY_TYPE_CHOICES = (
        ("APARTMENT", "Apartment"),
        ("PARKING", "Parking"),
        ("BOXROOM", "Boxroom"),
        ("COMMERCE", "Commerce"),
    )

    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="properties")
    category = models.CharField(max_length=50, choices=CATEGORY_TYPE_CHOICES)
    number = models.IntegerField(null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    floor = models.IntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.IntegerField(null=True, blank=True)
    layout = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.area is not None and self.price_per_sqm is not None:
            self.price = self.area * self.price_per_sqm
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category} #{self.number} в {self.block.complex.name}, к{self.block.block_number}"

    class Meta:
        db_table = "properties"

class PropertyPhotos(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_photos")
    photo_link = models.URLField()

    def __str__(self):
        return f"{self.photo_link}"

    class Meta:
        db_table = "property_photos"

class PropertyVideos(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_videos")
    video_link = models.URLField()

    class Meta:
        db_table = "property_videos"

    def __str__(self):
        return f"{self.video_link}"