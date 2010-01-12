from models import GenericReference
from haystack import indexes
from haystack import site

from django.conf import settings
if getattr(settings,'HAYSTACK_REAL_TIME',False) :
    search_index = indexes.RealTimeSearchIndex 
else :
    search_index = indexes.SearchIndex

class GenericIndex(search_index):
    title = indexes.CharField(model_attr='obj__get_display_name')
    content = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='creator__get_display_name')
    content_type = indexes.CharField(model_attr='content_type__model')

    #object_id = indexes.IntegerField(model_attr='object_id')

    #contributors = get_contributors
    #pub_date = indexes.DateTimeField(model_attr='pub_date')
    def get_queryset(self):
        return GenericReference.objects.filter(content_type__model__in=['wikipage', 'resource', 'profile', 'tggroup'])

site.register(GenericReference, GenericIndex)
