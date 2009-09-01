from django import template
from django.template.defaultfilters import truncatewords_html
from django.utils.html import urlize
from apps.plus_permissions.interfaces import NotViewable
register = template.Library()

class ValueTypes(dict):
    def __missing__(self, x):
        return self['plain']

def plain(value, truncate_at):
    return value, False

def html(value, truncate_at):
    #sanitize on output too?
    trunc_value = truncatewords_html(value, truncate_at)
    if len(trunc_value) < len(value):
        value = '<div class="truncated">%(trunc_value)s<span><a class="more" href="#">more</a><span></div><div class="untruncated">%(value)s<span><a class="less" href="#">less</a></span></div>' %(dict(value=value, trunc_value=trunc_value))
    return value, True

def url(value, truncate_at):
    if '@' not in value and 'http' not in value:
        value = 'http://' + value
    value = urlize(value)
    return value, True

value_types = ValueTypes({'plain': plain,
                          'url': url,
                          'html': html})


@register.inclusion_tag('plus_lib/editable_attribute.html')
def editable(label, obj, name, default, value_type='plain', truncate_at='100'):
    edit = obj.can_write(name)
    value = getattr(obj, name)
    #We use str to manange the NotViewable instance sometimes assigned by the TemplateSecureWrapper, since we have a utf-8 "value" here, if we do then str is okay, a
    if not value or value == NotViewable:
        value, no_escape = None, False
    else:
        value, no_escape = value_types[value_type](value, truncate_at) 
    show = edit or value
    if not value:
        value = default

    
    return {'label':label, 
            'obj':obj, 
            'name':name, 
            'show':show, 
            'edit':edit, 
            'value':value,
            'no_escape':no_escape}
