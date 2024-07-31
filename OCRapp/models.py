from django.db import models

# Create your models here.
class OCRImage(models.Model):
    image = models.ImageField(upload_to='images/')
    text = models.TextField(blank=True, null=True)
    