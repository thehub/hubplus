from django import template
register = template.Library()

@register.inclusion_tag('plus_lib/editable_attribute.html')
def editable(label, obj, name, default, no_escape="False"):
    edit = obj.can_write(name)
    value = getattr(obj, name)
    if not value:
        value = default
    show = edit or value
    if no_escape == "False":
        no_escape = False
    else:
        no_escape = True
    
    return {'label':label, 
            'obj':obj, 
            'name':name, 
            'show':show, 
            'edit':edit, 
            'value':value, 
            'no_escape':no_escape}
