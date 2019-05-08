from django.shortcuts import render, redirect
from django.contrib.postgres.search import SearchVector

from .models import Apartment
from .tasks import main


def cian_render(request, queryset=None):
    queryset = queryset or Apartment.objects.all()
    context = {'ads': queryset}
    return render(request, 'cian_table.html', context)

def delete_apartment(request):
    Apartment.objects.all().delete()
    return redirect('main:cian_render')

def load_apartment(request):
    Apartment.objects.all().delete()
    main.delay()
    return redirect('main:cian_render')

def search_apartment(request):
    search_vector = SearchVector('address', 'total_area', 'floor', 'price')
    queryset = Apartment.objects.annotate(search=search_vector) \
                                .filter(search=request.GET.get('query'))
    return cian_render(request, queryset)