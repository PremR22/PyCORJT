from django import forms
from .models import PassportImage

class OCRImageForm(forms.ModelForm):
    class Meta:
        model = PassportImage
        fields = ['front_image', 'back_image']