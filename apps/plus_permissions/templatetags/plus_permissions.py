from django import template

register = template.Library()

@register.inclusion_tag('permission_sliders.html')
def sliders(id, title, description):
    return {'id' : id,
            'title' : title,
            'description' : description,
            'target_id' : 'target'
         }
    
