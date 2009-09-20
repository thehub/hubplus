from apps.plus_links.models import  get_links_for

from django import template
register = template.Library()

@register.inclusion_tag('plus_links/list_and_form.html')
def plus_links(target_class, target_id) :

    return {
        'links' : [],
        'resource_class' : target_class,
        'resource_id' : target_id,
        }

      
