from django.shortcuts import render
from .models import User


def cian_render(request):
    return render(request, 'cian_table.html', {'users': User.objects.all()})
