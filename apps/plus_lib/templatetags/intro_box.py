
from django.template import get_library, Library, InvalidTemplateLibrary
from django.conf import settings
from apps.plus_lib.utils import area_from_path

register = Library()

@register.inclusion_tag('plus_lib/intro_box.html',takes_context=True)
def intro_box(context) :
    path = context['request'].path

    area = area_from_path(path)
    if area == 'member': 
        box = 'profiles/clients/%s/intro_box.html' % (settings.PROJECT_THEME)
    elif area == 'group' :
        box = 'plus_groups/clients/%s/groups/intro_box.html' % (settings.PROJECT_THEME)
    elif area == 'hub' :
        box = 'plus_groups/clients/%s/hubs/intro_box.html' % (settings.PROJECT_THEME)
    elif area == 'explore' :
        box = 'plus_explore/clients/%s/intro_box.html' % (settings.PROJECT_THEME)
    else : 
        box = '' 
    return {'relative_intro_box' : box, 'path' : path}
