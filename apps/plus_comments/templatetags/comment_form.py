from django import template
from apps.plus_permissions.interfaces import NotViewable
register = template.Library()

@register.inclusion_tag('plus_comments/reply_form.html')
def reply() :
    return {
        'person_name':person_name,
        'url' : url,
        }
