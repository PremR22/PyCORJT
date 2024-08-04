from django.db import models

# Create your models here.
class PassportImage(models.Model):
    front_image = models.ImageField(upload_to='images/')
    back_image = models.ImageField(upload_to='images/')
    front_text = models.TextField(blank=True, null=True)
    back_text = models.TextField(blank=True, null=True)

class PassportDetail(models.Model):
    passport_type = models.CharField(max_length=1)
    issuing_country = models.CharField(max_length=3)
    passport_number = models.CharField(max_length=9)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=3)
    sex = models.CharField(max_length=1)
    fathers_name = models.CharField(max_length=255)
    mothers_name = models.CharField(max_length=255)
    spouses_name = models.CharField(max_length=255)
    address = models.TextField()


    