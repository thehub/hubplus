from django.template import get_library, Library, InvalidTemplateLibrary
from django.conf import settings

register = Library()

@register.inclusion_tag('plus_lib/search_caption.html',takes_context=True)
def search_caption(context) :
    return {'search_caption':context['search_caption']}
