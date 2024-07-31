from django.urls import path
from . import views

urlpatterns = [
    path('', views.Hello, name='test'),
    path('upload/', views.upload_image, name='upload_image'),
    path('view/<int:pk>/', views.view_image, name='view_image'),
]
