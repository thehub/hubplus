from apps.plus_links.models import  get_links_for
from django.contrib.contenttypes.models import ContentType
from apps.plus_permissions.interfaces import secure_wrap

from django import template
register = template.Library()

@register.inclusion_tag('plus_links/list_and_form.html', takes_context=True)
def plus_links(context, target_class, target_id, errors=None, form_data=None) :
    """links should be checked for the view permission
    """
    target_cls = ContentType.objects.get(id=target_class).model_class()
    target = target_cls.objects.get(id=target_id)
    target = secure_wrap(target, context.get('request').user, interface_names=['CreateLink'])
    links = get_links_for(target, context)
    links = [(link, hasattr(link, 'delete')) for link in links]
    can_create = hasattr(target, 'create_Link')
    return {
        'links' :links,
        'target':target,
        'can_create':can_create,
        'target_id':target_id,
        'target_class_name':target_cls.__name__,
        'errors':errors,
        'form_data':form_data
        }
