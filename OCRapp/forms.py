from django import forms
from .models import PassportImage, PassportDetail

class OCRImageForm(forms.ModelForm):
    class Meta:
        model = PassportImage
        fields = ['front_image', 'back_image']

class PassportDetailsForm(forms.ModelForm):
    class Meta:
        model = PassportDetail
        fields = ['passport_type', 'issuing_country', 'passport_number', 'name', 'surname', 'dob', 'expiry_date', 'nationality', 'sex', 'fathers_name', 'mothers_name', 'spouses_name', 'address']