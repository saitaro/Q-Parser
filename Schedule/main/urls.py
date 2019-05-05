from django.urls import path
from .views import cian_render


app_name = 'main'

urlpatterns = [
    path('', cian_render, name='cian_render')
]