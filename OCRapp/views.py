from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from datetime import datetime
from PIL import Image
import numpy as np
import json
import pytesseract
import cv2
import re

from .forms import OCRImageForm
from .models import PassportImage, PassportDetail

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
            return redirect('OCRapp:view_image', passport.id)
    else:
        form = OCRImageForm()
    return render(request, 'OCRapp/upload_image.html', {'form': form})

def view_image(request, pk):
    passport = PassportImage.objects.get(pk=pk)
    return render(request, 'OCRapp/view_image.html', {'passport' : passport})

def view_clean_data(request, pk):
    passport = PassportImage.objects.get(pk=pk)

    passport_type, issuing_country, passport_number, firstname, surname, dob, expiry_date, nationality, gender = front_clean_data(passport.front_text)
    father_name, mother_name, spouse_name, address = back_clean_data(passport.back_text)

    passport_detail, created = PassportDetail.objects.get_or_create(
        passport_number=passport_number,
        defaults={
            'passport_type': passport_type,
            'issuing_country': issuing_country,
            'name': firstname,
            'surname': surname,
            'dob': dob,
            'expiry_date': expiry_date,
            'nationality': nationality,
            'sex': gender,
            'fathers_name': father_name,
            'mothers_name': mother_name,
            'spouses_name': spouse_name,
            'address': address
        }
    )

    return render(request, 'OCRapp/view_clean_data.html', {'passport_detail': passport_detail})

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
    return extract_data(mrz_text)  

def back_clean_data(back_raw_text):
    father_name, mother_name, spouse_name = extract_names(back_raw_text)
    cleaned_text = clean_data(back_raw_text)
    address = extract_address(cleaned_text)

    return (
        father_name,
        mother_name,
        spouse_name,
        address
    )

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
    
    current_format = "%y%m%d"
    desired_format = "%Y-%m-%d"

    line1 = mrz_lines[0]
    line2 = mrz_lines[1]

    passport_type = line1[0:1]
    issuing_country = line1[2:5]
    name_parts = line1[5:].split('<')
    surname = name_parts[0].replace('<', ' ').strip()
    surname = re.sub(r'[a-z]', '', surname)
    firstname = ' '.join(name_parts[1:]).replace('<', ' ').strip()
    firstname = re.sub(r'[a-z]', '', firstname)

    passport_number = line2[0:8]
    nationality = line2[10:13]
    dob = line2[13:19]
    dob = extract_date(dob, current_format, desired_format)
    gender = line2[20] 
    expiry_date = line2[21:27]
    expiry_date = extract_date(expiry_date, current_format, desired_format)

    return (
        passport_type,
        issuing_country,
        passport_number,
        firstname,
        surname,
        dob,
        expiry_date,
        nationality,
        gender
    )
    

def extract_date(date, current_format, desired_format):
    try:
        date_obj = datetime.strptime(date, current_format)
        return date_obj.strftime(desired_format)
    except Exception:
        return None


def extract_address(cleaned_text):
    address_pattern = re.compile(r"([A-Z\s,]*?PIN\s*:\s*\d{6}[A-Z\s,]*)", re.DOTALL)
    matches = address_pattern.findall(cleaned_text)
    if matches:
        address = matches[0].strip()
        return address
    else:
        return None
    
def extract_names(back_raw_text):
    names = []
    lines = back_raw_text.split('\n')
    for line in lines:
        line = line.strip()
        line = re.sub(r'\b\w*[a-z]\w*\b', '', line)
        line = re.sub(r'\s+', ' ', line).strip()
        if re.fullmatch(r"[A-Z\s,.]*", line):
            line = line.replace('.', "")
            line = line.rstrip()
            names.append(line)
    name_list =  [name for name in names if name]
    filtered_names = [
        name for name in name_list
        if len(name) > 3
    ]
    father_name = filtered_names[0]
    mother_name = filtered_names[1]
    spouse_name = filtered_names[2]

    return (
        father_name,
        mother_name,
        spouse_name
    )

def export_to_JSON(request, pk):
    passport_detail = get_object_or_404(PassportDetail, pk=pk)
    custom_data = {
        'passportType': passport_detail.passport_type,
        'issuingCountry': passport_detail.issuing_country,
        'passportNumber': passport_detail.passport_number,
        'firstName': passport_detail.name,
        'surname': passport_detail.surname,
        'dateOfBirth': passport_detail.dob.isoformat() if passport_detail.dob else None,
        'expiryDate': passport_detail.expiry_date.isoformat() if passport_detail.expiry_date else None,
        'nationality': passport_detail.nationality,
        'gender': passport_detail.sex,
        'fatherName': passport_detail.fathers_name,
        'motherName': passport_detail.mothers_name,
        'spouseName': passport_detail.spouses_name,
        'address': passport_detail.address,
    }

    json_data = json.dumps(custom_data, indent=4)
    return JsonResponse(json.loads(json_data), safe=False)

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
