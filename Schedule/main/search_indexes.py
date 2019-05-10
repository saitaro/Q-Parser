from .models import Apartment
from haystack import indexes
from .models import Apartment


class ApartmentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # address = indexes.CharField(model_attr='address')
    total_area = indexes.IntegerField(model_attr='total_area')
    price = indexes.IntegerField(model_attr='price')
    content_auto = indexes.EdgeNgramField(model_attr='address')

    def get_model(self):
        return Apartment

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
