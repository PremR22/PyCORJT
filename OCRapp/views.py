from django.shortcuts import render, HttpResponse, redirect
from PIL import Image
import numpy as np
import pytesseract
import cv2
import re

from .forms import OCRImageForm
from .models import PassportImage

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')

def upload_image(request):
    if request.method == 'POST':
        form = OCRImageForm(request.POST, request.FILES)
        if form.is_valid():
            passport = form.save()

            front_image_path = passport.front_image.path
            back_image_path = passport.back_image.path

            processed_front_image = process_image(front_image_path)
            processed_back_image = process_image(back_image_path)

            passport.back_text = extract_text(processed_back_image)
            passport.front_text = extract_text(processed_front_image)

            passport.save()
            front_clean_data(passport.front_text)
            back_clean_data(passport.back_text)
            return redirect('view_image', passport.id)
    else:
        form = OCRImageForm()
    return render(request, 'OCRapp/upload_image.html', {'form': form})

def view_image(request, pk):
    passport = PassportImage.objects.get(pk=pk)
    return render(request, 'OCRapp/view_image.html', {'passport' : passport})

def view_clean_data(request):
    return render(request, 'OCRapp/view_clean_data.html')

def process_image(image_path):
    image = cv2.imread(image_path)         
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    processed_img = Image.fromarray(image)
    return processed_img

def extract_text(processed_image):
    raw_text = pytesseract.image_to_string(processed_image)
    return raw_text

def clean_data(raw_text):
    lowercase_pattern = re.compile(r"\b[a-z]+\b")
    cleaned_text = lowercase_pattern.sub(' ', raw_text)

    cleaned_text = cleaned_text.replace('\n', ' ').replace('\r', ' ')

    cleaned_text = re.sub(r'\s*,\s*', ',', cleaned_text)
    cleaned_text = re.sub(r'[^a-zA-Z0-9 ,:/]', ' ', cleaned_text)
    cleaned_text = re.sub(r'\s/\s', '', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    print("cleaned text")
    print(cleaned_text)

    return cleaned_text


def front_clean_data(front_raw_text):
    cleaned_text = clean_data(front_raw_text)

    date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}(?:st|nd|rd|th)?\s+\w+,\s+\d{4})\b'
    date_matches = re.findall(date_pattern, cleaned_text)
    if date_matches:
        dob = date_matches[0]
        print("Extracted Date of Birth:")
        print(dob)
    else:
        print("DOB not found.")

    passport_pattern = r'[A-Z](?:\s*\d\s*){7}'
    pass_matches = re.findall(passport_pattern, cleaned_text)
    if pass_matches:
        passport_number = re.sub(r'\s+', '', pass_matches[0])
        print("Extracted Passport Number:")
        print(passport_number)
    else:
        print("Passport number not found.")

    extract_name(cleaned_text)

    
def back_clean_data(back_raw_text):
    cleaned_text = clean_data(back_raw_text)

    address_pattern = re.compile(r"([A-Z\s,]*?PIN\s*:\s*\d{6}[A-Z\s,]*)", re.DOTALL)
    matches = address_pattern.findall(cleaned_text)
    if matches:
        address = matches[0].strip()  # Get the first match and strip any surrounding whitespace
        print("Extracted Address:")
        print(address)
    else:
        print("Address not found.")
    
    extract_name(cleaned_text)


def extract_name(cleaned_text):
    name_pattern = r'\b[A-Z][A-Z\'-]*\b'
    names = re.findall(name_pattern, cleaned_text)
    filtered_names = [
        re.sub(r'[^\w\'-]', '', name)
        for name in names
    ]
    filtered_names = [
        name for name in filtered_names
        if len(name) > 3 and ' ' not in name
    ]
    if filtered_names:
        print("Extracted Names:")
        print(filtered_names)
    else:
        print("Passport number not found.")


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
