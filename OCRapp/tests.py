from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import PassportImage

# Create your tests here.
class TestOCRappView(TestCase):

    def setUp(self):
        dummy_front_img = SimpleUploadedFile(
            "front_passport.jpg", 
            b"dummy_content", 
            content_type="image/jpeg")
        dummy_back_img = SimpleUploadedFile("back_passport.jpg", b"dummy_content", content_type="image/jpeg")
        self.passport_image = PassportImage.objects.create(
            front_image = dummy_front_img,
            back_image = dummy_back_img,
            front_text="P<INDDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<\nG12345678IND8001012M2501015<<<<<<<<<<<<<<06", 
            back_text="DOE JOHN SR.\nSMITH JANE\nDOE JANE\n123 EXAMPLE STREET, MUMBAI, MAHARASHTRA PIN:400001, INDIA",
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

  


