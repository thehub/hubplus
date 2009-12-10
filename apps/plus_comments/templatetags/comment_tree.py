
from django import template
from apps.plus_permissions.interfaces import NotViewable, is_not_viewable
from django.conf import settings


register = template.Library()

@register.inclusion_tag('plus_comments/comment_tree.html', takes_context=True)
def comment_tree(context, target, name) :
    if is_not_viewable(target,'comment') :
        can_comment = False
    else :
        can_comment = True

    if name == 'Group' :
        if target.get_inner().is_hub_type() :
            name = settings.HUB_NAME

    user = context['request'].user
    return {
        'target':target,
        'target_type' : name,
        'can_comment':can_comment,
        'user':user,
        }

