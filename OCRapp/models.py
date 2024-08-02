from django.db import models

# Create your models here.
class PassportImage(models.Model):
    front_image = models.ImageField(upload_to='images/')
    back_image = models.ImageField(upload_to='images/')
    front_text = models.TextField(blank=True, null=True)
    back_text = models.TextField(blank=True, null=True)

class PassportDetails(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    passport_no = models.CharField(max_length=20, unique=True)
    nationality = models.CharField(max_length=100)
    dob = models.DateField()
    address = models.CharField(max_length=500)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)



    