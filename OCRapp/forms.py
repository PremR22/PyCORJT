from django import forms
from .models import PassportImage, PassportDetails

class OCRImageForm(forms.ModelForm):
    class Meta:
        model = PassportImage
        fields = ['front_image', 'back_image']

class PassportDetailsForm(forms.ModelForm):
    class Meta:
        model = PassportDetails
        fields = ['first_name', 'last_name', 'passport_no', 'nationality', 'dob', 'address', 'father_name', 'mother_name']