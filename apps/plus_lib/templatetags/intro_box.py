from django.template import get_library, Library, InvalidTemplateLibrary
from django.conf import settings
register = Library()

@register.inclusion_tag('plus_lib/intro_box.html',takes_context=True)
def intro_box(context) :
    path = context['request'].path
    if 'members' in path :
        box = 'profiles/clients/%s/intro_box.html' % (settings.PROJECT_THEME)
    elif 'group' in path :
        box = 'plus_groups/clients/%s/groups/intro_box.html' % (settings.PROJECT_THEME)
    elif 'hub' in path or 'region' in path :
        box = 'plus_groups/clients/%s/hubs/intro_box.html' % (settings.PROJECT_THEME)
    elif 'explore' in path or 'resources' in path :
        box = 'plus_explore/clients/%s/intro_box.html' % (settings.PROJECT_THEME)
    else : 
        box = '' 
    return {'relative_intro_box' : box, 'path' : path}
