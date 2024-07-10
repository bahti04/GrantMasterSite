from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sort/', views.sort, name='sort'),
    path('process/', views.process_file, name='process_file'),
    path('download/<str:file_path>/', views.download_file, name='download_file'),
]