from django.shortcuts import render, HttpResponse, redirect
from PIL import Image
import numpy as np
import datefinder
import pytesseract
import cv2
import re

from .forms import OCRImageForm
from .models import OCRImage

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Create your views here.
def Hello(request):
    return HttpResponse('Hello World')

def homepage(request):
    return render(request, 'homepage.html')

def upload_image(request):
    if request.method == 'POST':
        form = OCRImageForm(request.POST, request.FILES)
        if form.is_valid():
            passport = form.save()
            image_path = passport.image.path
            image = cv2.imread(image_path)
            
            kernel = np.ones((1, 1), np.uint8)
            image = cv2.dilate(image, kernel, iterations=1)
            kernel = np.ones((1, 1), np.uint8)
            image = cv2.erode(image, kernel, iterations=1)
            image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
            image = cv2.medianBlur(image, 3)

            processed_img = Image.fromarray(image)
            processed_img.save("media/temp/processed_img.jpg")

            raw_text = pytesseract.image_to_string(processed_img)       

            passport.text = raw_text
            passport.save()

            clean_data(raw_text)
            return redirect('view_image', passport.id)
    else:
        form = OCRImageForm()
    return render(request, 'OCRapp/upload_image.html', {'form': form})

def view_image(request, pk):
    passport = OCRImage.objects.get(pk=pk)
    return render(request, 'OCRapp/view_image.html', {'passport' : passport})

def clean_data(raw_text):
    cleaned_text = []
    date_pattern = r'\d{2}-\d{2}-\d{4}'
    passport_pattern = r'\b[A-Z][0-9]{8}\b'
            
    print(raw_text)

    passport_no = re.search(passport_pattern, raw_text)
    print(passport_no)

    date = re.search(date_pattern, raw_text)
    if date:
        dates = date.group()
        print(dates)
    else:
        print("No dates")
        for text in raw_text.split():
            if not text.islower() or text.isnumeric():
                cleaned_text.append(text)


def bounding_box(image_path):
    results = []
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (3,13))
    dilate = cv2.dilate(thresh, kernal, iterations=1)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h > 5 and w > 5:
            roi = image[y:y+h, x:x+h]
            cv2.rectangle(image, (x, y), (x+w, y+h), (36, 255, 12), 2)
            ocr_result = pytesseract.image_to_string(roi)
            ocr_result = ocr_result.split("\n")
            for item in ocr_result:
                item = item.strip().replace("\n", "")
                item = item.split(" ")[0]
                if len(item):
                    if item.isupper() or item.isnumeric():
                        results.append(item)
    print(results)
    cv2.imwrite("media/temp/bbox_img.jpg", image)
