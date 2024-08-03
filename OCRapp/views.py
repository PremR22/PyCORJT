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
            return redirect('view_image', passport.id)
    else:
        form = OCRImageForm()
    return render(request, 'OCRapp/upload_image.html', {'form': form})

def view_image(request, pk):
    passport = PassportImage.objects.get(pk=pk)
    return render(request, 'OCRapp/view_image.html', {'passport' : passport})

def view_clean_data(request, pk):
    passport = PassportImage.objects.get(pk=pk)
    front_clean_data(passport.front_text)
    back_clean_data(passport.back_text)
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

    return cleaned_text

def front_clean_data(front_raw_text):
    mrz_text = extract_mrz(front_raw_text)
    print("Front raw: ", front_raw_text)
    print("mrz_text", mrz_text)
    extract_data(mrz_text)

def back_clean_data(back_raw_text):
    cleaned_text = clean_data(back_raw_text)
    address = extract_address(cleaned_text)
    names = extract_name(cleaned_text)

    print("Names: ", names)
    print("Address: ", address)

def extract_mrz(front_raw_text):
    lines = front_raw_text.split('\n')
    mrz_lines = []
    for line in lines:
        line = line.strip()
        line = line.replace(" ", "")
        if len(line) >= 30 and all(c.isalnum() or c in "<>" for c in line):
            mrz_lines.append(line)
    #mrz_lines = [line for line in lines if re.match(r'^[A-Z0-9<>]{44,90}$', line)]
    mrz_text = '\n'.join(mrz_lines)
    return mrz_text

def extract_data(mrz_text):
    mrz_lines = mrz_text.split('\n')
    if len(mrz_lines) < 2:
        raise ValueError("Not enough MRZ lines to parse")
    
    line1 = mrz_lines[0]
    line2 = mrz_lines[1]

    passport_type = line1[0:1]
    issuing_country = line1[2:5]
    name_parts = line1[5:].split('<')
    surname = name_parts[0].replace('<', ' ').strip()
    firstname = ' '.join(name_parts[1:]).replace('<', ' ').strip()

    passport_number = line2[0:8]
    nationality = line2[10:13]
    dob = line2[13:19]
    gender = line2[20]
    expiry_date = line2[21:27]

    print("Passport Type: ", passport_type)
    print("Issuing Country: ", issuing_country)
    print("Passport Number: ", passport_number)
    print("Name: ", firstname)
    print("Surname: ", surname)
    print("DOB: ", dob)
    print("Expiry Date: ", expiry_date)
    print("Nationality: ", nationality)
    print("Sex: ", gender)


def extract_dob(cleaned_text):
    date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}(?:st|nd|rd|th)?\s+\w+,\s+\d{4})\b'
    date_matches = re.findall(date_pattern, cleaned_text)
    if date_matches:
        dob = date_matches[0]
        return dob
    else:
        return "not found"
    
def extract_passport_no(cleaned_text):
    passport_pattern = r'[A-Z](?:\s*\d\s*){7}'
    pass_matches = re.findall(passport_pattern, cleaned_text)
    if pass_matches:
        passport_number = re.sub(r'\s+', '', pass_matches[0])
        return passport_number
    else:
        return "not found"

def extract_address(cleaned_text):
    address_pattern = re.compile(r"([A-Z\s,]*?PIN\s*:\s*\d{6}[A-Z\s,]*)", re.DOTALL)
    matches = address_pattern.findall(cleaned_text)
    if matches:
        address = matches[0].strip()  # Get the first match and strip any surrounding whitespace
        return address
    else:
        return "not found"

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
        return filtered_names
    else:
        return "not found"


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
