from django import template
register = template.Library()

@register.inclusion_tag('plus_lib/ajax_select.html')
def ajax_select(name, options, current_value):
    # making this a fairly generic component without commitments to *what* we're updating
    # XXX in future we'd like the option that "options" is a URL to make a live ajax call, 
    # but not necessary today
    return {'name':name, 'options':options, 'current':current_value}
