from apps.plus_tags.models import  tag_add, tag_delete, get_tags, tag_autocomplete

from django import template
register = template.Library()

@register.inclusion_tag('plus_tags/list.html')
def view_plus_tag(label, tag_type, tagged, tagger) :
    """
    """
    tags = get_tags(tagged=tagged, tagger=tagger, tag_type=tag_type)
    return {'label':label,
            'tags' : tags, 
            'tagged_class' : tagged.obj().__class__.__name__ ,
            'tagged_id' : tagged.id,
            'tag_type' : tag_type}


@register.inclusion_tag('plus_tags/list_and_form.html')
def plus_tag(label, tag_type, tagged, tagger) :
    """XXX update to deal with tagged for and tagged by
    """

    tags = get_tags(tagged=tagged, tagger=tagger, tag_type=tag_type)
    return {'label':label,
            'tags' : tags, 
            'tagged_class' : tagged.obj().__class__.__name__ ,
            'tagged_id' : tagged.id,
            'tag_type' : tag_type}
