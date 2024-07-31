from django.shortcuts import render, HttpResponse, redirect
from PIL import Image
import pytesseract
import cv2

from .forms import OCRImageForm
from .models import OCRImage

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Create your views here.
def Hello(request):
    return HttpResponse('Hello World')

def upload_image(request):
    if request.method == 'POST':
        form = OCRImageForm(request.POST, request.FILES)
        if form.is_valid():
            passport = form.save()
            original_img = cv2.imread(passport.image.path)
            inverted_img = cv2.bitwise_not(original_img)
            
            processed_img = Image.fromarray(inverted_img)

            text = pytesseract.image_to_string(processed_img)
            passport.text = text
            passport.save()
            return redirect('view_image', passport.id)
    else:
        form = OCRImageForm()
    return render(request, 'OCRapp/upload_image.html', {'form': form})

def view_image(request, pk):
    passport = OCRImage.objects.get(pk=pk)
    return render(request, 'OCRapp/view_image.html', {'passport' : passport})