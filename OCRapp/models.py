from django.db import models

# Create your models here.
class OCRImage(models.Model):
    image = models.ImageField(upload_to='images/')
    text = models.TextField(blank=True, null=True)

class Passport(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    passport_no = models.CharField(max_length=20, unique=True)
    nationality = models.CharField(max_length=100)
    dob = models.DateField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)



    