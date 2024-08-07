# PyCORJT

PyCORJT is a simple web app which extracts & displays data from passport images using OCR and exports it as JSON file.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Steps

1. Clone the repository

```
git clone https://github.com/PremR22/PyCORJT.git
```

2. Navigate to the Project Directory

```
cd PyCORJT
```

3. Create & Activate a Virtual Environment

```
python -m venv ocr-env
ocr-env\Scripts\activate
```

4. Install dependencies

```
pip install -r requirements.txt
```

5. Run migrations

```
python manage.py migrate
```

6. Start the server

```
python manage.py runserver
```

Then open http://localhost:8000/ocr/ in your browser to explore API.

## Running the tests

I also went ahead and wrote tests for my Models, Forms and some of my views. To run tests, simply run this command.

```
python manage.py test
```

## Built With

- **[Django](https://www.djangoproject.com/)**: The web framework used for developing the web application.
- **[numpy](https://numpy.org/)**: A library used for numerical operations.
- **[Pillow](https://pillow.readthedocs.io/en/stable/)**: A library used for image processing.
- **[pytesseract](https://github.com/madmaze/pytesseract)**: A library used for Optical Character Recognition (OCR) with Tesseract.

  
## Acknowledgments

* **[Python Tutorials for Digital Humanities](https://www.youtube.com/playlist?list=PL2VXyKi-KpYuTAZz__9KVl1jQz74bDG7i)** - the GOAT which made this project possible. The best resource one could ask for doing anything OCR related in python.

