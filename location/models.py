from django.db import models

# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cities'

class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}, {self.city.name}"

    class Meta:
        db_table = 'districts'