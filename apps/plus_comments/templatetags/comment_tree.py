
from django import template
from apps.plus_permissions.interfaces import NotViewable
from django.conf import settings

register = template.Library()

@register.inclusion_tag('plus_comments/comment_tree.html', takes_context=True)
def comment_tree(context, target, name) :

    try :
        target.comment
        can_comment = True
    except PlusPermissionsNoAccessException :
        can_comment = False

    if name == 'Group' :
        if target.get_inner().is_hub_type() :
            name = settings.HUB_NAME

    return {
        'target':target,
        'target_type' : name,
        'can_comment':can_comment,
        }

