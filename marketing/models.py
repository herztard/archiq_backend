from django.db import models

# Create your models here.
class Banner(models.Model):
    title = models.CharField(max_length=50)
    subtitle = models.CharField(max_length=255)
    image_link = models.URLField()
    target_url = models.URLField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'banners'