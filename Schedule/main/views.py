from django.shortcuts import render
from .models import Apartment


def cian_render(request):
    return render(request, 'cian_table.html', {'ads': Apartment.objects.all()})
