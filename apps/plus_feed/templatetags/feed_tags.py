from django.core.urlresolvers import reverse
from django import template
from apps.plus_feed.models import FeedItem

register = template.Library()

from django.template.defaultfilters import stringfilter

import re


@stringfilter
def at_tags(val,*args,**kwargs) :
    if not '@' in val :
        return val
    rx = re.compile(r"(\@([A-Za-z0-9_\.\']+))")
    sub = r"""<a href='/members/\2/#tabview=updates_feed'>@\2</a>"""
    return rx.sub(sub, val)

register.filter('at_tags',at_tags)


@register.inclusion_tag("plus_feed/one_item_inner.html", takes_context=True)
def one_item(context, item_id, stand_alone=False) :
    request = context['request']
    user = request.user

    fi = FeedItem.objects.plus_get(user, id=item_id)
    return {"item":fi, 
            "current_user":user,
            "request":request,
            "stand_alone":stand_alone,
            "prefix_sender":True}
