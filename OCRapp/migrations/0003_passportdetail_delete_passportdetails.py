# Generated by Django 5.0.7 on 2024-08-04 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OCRapp', '0002_passportdetails_passportimage_delete_ocrimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='PassportDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('passport_type', models.CharField(max_length=1)),
                ('issuing_country', models.CharField(max_length=3)),
                ('passport_number', models.CharField(max_length=9)),
                ('name', models.CharField(max_length=255)),
                ('surname', models.CharField(max_length=255)),
                ('dob', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('nationality', models.CharField(max_length=3)),
                ('sex', models.CharField(max_length=1)),
                ('fathers_name', models.CharField(max_length=255)),
                ('mothers_name', models.CharField(max_length=255)),
                ('spouses_name', models.CharField(max_length=255)),
                ('address', models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name='PassportDetails',
        ),
    ]
