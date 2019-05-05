from django.shortcuts import render, redirect

from .models import Apartment
from .tasks import main

def cian_render(request):
    return render(request, 'cian_table.html', {'ads': Apartment.objects.all()})

def delete_apartment(request):
    Apartment.objects.all().delete()
    return redirect('main:cian_render')

def load_apartment(request):
    Apartment.objects.all().delete()
    main.delay()
    return redirect('main:cian_render')
