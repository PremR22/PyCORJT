from django import forms
from .models import OCRImage

class OCRImageForm(forms.ModelForm):
    class Meta:
        model = OCRImage
        fields = ['image']