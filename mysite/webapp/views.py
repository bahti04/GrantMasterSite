from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'webapp/home.html')

def before_translation(request):
    return HttpResponse("Страница до перевода")

def after_translation(request):
    return HttpResponse("Страница после перевода")

