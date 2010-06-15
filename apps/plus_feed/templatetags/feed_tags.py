from django.core.urlresolvers import reverse
from django import template

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


