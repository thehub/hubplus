from apps.plus_tags.models import  tag_add, tag_delete, get_tags, tag_autocomplete

from django import template
register = template.Library()

@register.inclusion_tag('plus_tags/list_and_form.html')
def plus_tag(dd_id, tag_type, target, tagger) :
    print "TRTRTRT"
    tags = get_tags(tagged = target, tagger = tagger, tag_type = 'interest')
    print "JKJKJKJ"
    print tags
    print target.__class__.__name__
    print target.id
    print dd_id
    print tag_type
    print "WEWEW"
    return {'tags' : tags, 
            'target_class' : target.__class__.__name__ ,
            'target_id' : target.id,
            'dd_id' : dd_id,
            'tag_type' : tag_type}


