from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('upload/', views.upload_image, name='upload_image'),
    path('view/<int:pk>/', views.view_image, name='view_image'),
]
