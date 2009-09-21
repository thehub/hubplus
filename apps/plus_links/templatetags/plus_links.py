from apps.plus_links.models import  get_links_for_type_and_id
from django.contrib.contenttypes.models import ContentType

from django import template
register = template.Library()

@register.inclusion_tag('plus_links/list_and_form.html')
def plus_links(target_class, target_id) :

    links = get_links_for_type_and_id(target_class, target_id)
    
    return {
        'links' : links,
        'target_class' : target_class,
        'target_id' : target_id,
        'target_class_name' : ContentType.objects.get(id=target_class).model
        }
