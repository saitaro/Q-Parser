from django.shortcuts import render, redirect
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model

from .models import Apartment
from .tasks import main


def cian_render(request, queryset=None):
    query = request.GET.get('query')
    if query:
        search_vector = SearchVector('address', 'total_area', 'floor', 'price')
        queryset = Apartment.objects.annotate(search=search_vector) \
                                    .filter(search=request.GET.get('query'))
    else:
        queryset = queryset or Apartment.objects.all()

    paginator = Paginator(queryset, 20)
    page = request.GET.get('page')
    
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    index = items.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]

    User = get_user_model()
    last = User.objects.last()
    
    context = {
        'items': items,
        'page_range': page_range,
        'ads_count': queryset.count(),
        'query': query,
        'max_index': max_index,
        'last': last,
        'favs': request.user.favorites.all() if request.user.is_authenticated else {},
    }
    return render(request, 'cian_table.html', context)

def delete_apartment(request):
    Apartment.objects.all().delete()
    return redirect('main:cian_render')

def load_apartment(request):
    Apartment.objects.all().delete()
    main.delay()
    return redirect('main:cian_render')
