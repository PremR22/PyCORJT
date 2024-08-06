from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import PassportImage, PassportDetail
from .forms import OCRImageForm, PassportDetailsForm
import datetime

# Create your tests here.
class PassportImageModelTest(TestCase):
    def setUp(self):
        dummy_front_img = SimpleUploadedFile("front_passport.jpg", b"dummy_content", content_type="image/jpeg")
        dummy_back_img = SimpleUploadedFile("back_passport.jpg", b"dummy_content", content_type="image/jpeg")
        self.passport_image = PassportImage.objects.create(
            front_image = dummy_front_img,
            back_image = dummy_back_img,
            front_text="Sample Front Text", 
            back_text="Sample Back Text"
            )
        
    def test_passport_image_creation(self):
        self.assertIsInstance(self.passport_image, PassportImage)
        self.assertEqual(self.passport_image.front_text, "Sample Front Text")
        self.assertEqual(self.passport_image.back_text, "Sample Back Text")

class PassportDetailModelTest(TestCase):
    def setUp(self):
        self.passport_detail = PassportDetail.objects.create(
            passport_type = "P",
            issuing_country = "IND",
            passport_number = "A12345678",
            name = "JOHN",
            surname = "DOE",
            dob = datetime.date(1990, 1, 1),
            expiry_date = datetime.date(2030, 1, 1),
            nationality = "IND",
            sex = "M",
            fathers_name = "JOHN DOE SR",
            mothers_name = "MARY SMITH",
            spouses_name = "JANE DOE",
            address = "123 EXAMPLE STREET, MUMBAI, MAHARASHTRA PIN:400001, INDIA"
        )
    
    def test_passport_detail_creation(self):
        self.assertIsInstance(self.passport_detail, PassportDetail)
        self.assertEqual(self.passport_detail.name, "JOHN")
        self.assertEqual(self.passport_detail.surname, "DOE")
        self.assertEqual(self.passport_detail.passport_number, "A12345678")
        self.assertEqual(self.passport_detail.nationality, "IND")
        self.assertEqual(self.passport_detail.sex, "M")
        self.assertEqual(self.passport_detail.fathers_name, "JOHN DOE SR")
        self.assertEqual(self.passport_detail.mothers_name, "MARY SMITH")
        self.assertEqual(self.passport_detail.spouses_name, "JANE DOE")
        self.assertEqual(self.passport_detail.address, "123 EXAMPLE STREET, MUMBAI, MAHARASHTRA PIN:400001, INDIA")

class OCRImageFormTest(TestCase):
    def setUp(self):
        self.front_image = SimpleUploadedFile(name="front_passport.jpg", content=b"", content_type="image/jpeg")
        self.back_image = SimpleUploadedFile(name="back_passport.jpg", content=b"", content_type="image/jpeg")
    
    def test_ocr_image_form_is_valid(self):   
        form_data = {
            'front_image' : self.front_image,
            'back_image' : self.back_image,
        }
        form = OCRImageForm(data=form_data, files=form_data)
        self.assertTrue(form.is_valid())
        passport_image = form.save()
        self.assertIsInstance(passport_image, PassportImage)

    def test_ocr_image_form_is_invalid(self):
        form = OCRImageForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('front_image', form.errors)
        self.assertIn('back_image', form.errors)

class PassportDetailsFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'passport_type': 'P',
            'issuing_country': 'IND',
            'passport_number': 'A12345678',
            'name': 'JOHN',
            'surname': 'DOE',
            'dob': datetime.date(1990, 1, 1),
            'expiry_date': datetime.date(2030, 1, 1),
            'nationality': 'IND',
            'sex': 'M',
            'fathers_name': 'JOHN DOE SR',
            'mothers_name': 'MARY SMITH',
            'spouses_name': 'JANE DOE',
            'address': '123 EXAMPLE STREET, MUMBAI, MAHARASHTRA PIN:400001, INDIA',
        }

    def test_passport_details_form_is_valid(self):
        form = PassportDetailsForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        passport_detail = form.save()
        self.assertIsInstance(passport_detail, PassportDetail)

    def test_passport_details_form_is_invalid(self):
        form = PassportDetailsForm(data={})
        self.assertTrue(form.is_valid())
        required_fields = [
        'passport_type', 'issuing_country', 'passport_number', 'name', 'surname',
        'dob', 'expiry_date', 'nationality', 'sex', 'fathers_name', 'mothers_name',
        'spouses_name', 'address'
        ]
        for field in required_fields:
            self.assertIn(field, form.errors)

class OCRappViewTest(TestCase):
    def setUp(self):
        dummy_front_img = SimpleUploadedFile("front_passport.jpg", b"dummy_content", content_type="image/jpeg")
        dummy_back_img = SimpleUploadedFile("back_passport.jpg", b"dummy_content", content_type="image/jpeg")
        self.passport_image = PassportImage.objects.create(
            front_image = dummy_front_img,
            back_image = dummy_back_img,
            front_text="P<INDDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<\nG12345678IND8001012M2501015<<<<<<<<<<<<<<06", 
            back_text="DOE JOHN SR.\nMARY SMITH\nJANE DOE\n123 EXAMPLE STREET, MUMBAI, MAHARASHTRA PIN:400001, INDIA",
            )

    def test_homepage_view(self):
        response = self.client.get(reverse('OCRapp:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to PyCORJT")

    def test_upload_image_view(self):
        response = self.client.get(reverse('OCRapp:upload_image'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Insert your Passport Images")

    def test_view_image_view(self):
        response = self.client.get(reverse('OCRapp:view_image', args=[self.passport_image.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Extracted Raw Text")

    def test_view_clean_data_view(self):
        response = self.client.get(reverse('OCRapp:view_clean_data', args=[self.passport_image.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cleaned Text")   

  
