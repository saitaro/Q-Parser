from django.urls import path
from .views import (cian_render, delete_apartment,
                    load_apartment, 
                    # search_apartment
                    )


app_name = 'main'

urlpatterns = [
    path('', cian_render, name='cian_render'),
    path('delete', delete_apartment, name='delete_apartment'),
    path('load', load_apartment, name='load_apartment'),
    # path('search', search_apartment, name='search_apartment'),
]