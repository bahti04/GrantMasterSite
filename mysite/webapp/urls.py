from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('before_translation/', views.before_translation, name='before_translation'),
    path('after_translation/', views.after_translation, name='after_translation'),
]