from django import template
register = template.Library()

@register.inclusion_tag('plus_lib/editable_attribute.html')
def editable(label, obj, name, default):
    edit = obj.can_write(name)
    value = getattr(obj, name, default)
    show = edit or str(value)
    return {'label':label, 'obj':obj, 'name':name, 'show':show, 'edit':edit, 'value':value}
