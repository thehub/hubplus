from apps.plus_tags.models import  tag_add, tag_delete, get_tags, tag_autocomplete, tag_counts, keyword_sort, scale_tag_weights

from apps.plus_permissions.api import TemplateSecureWrapper

from django import template
register = template.Library()


@register.inclusion_tag('plus_tags/tag_cloud.html')
def tag_cloud(n, size, search_types, tag_search_url='explore_filtered'):
    if not search_types:
        search_types = None
    tags = get_tags(tagged=search_types)
    counts = tag_counts(n=n, tag_set=tags)
    if counts :
        tag_levels = scale_tag_weights(counts)
        tag_levels.sort(keyword_sort)
    else :
        tag_levels = []
    return {'tags':tag_levels, 'size':size, 'tag_search_url':tag_search_url}


@register.inclusion_tag('plus_tags/list.html')
def view_plus_tag(label, tag_type, tagged, tagged_for) :
    """
    """
    if not tag_type:
        tag_type = None
    if not tagged_for:
        tagged_for = None
    if tagged == '' :
        tagged = None
    tags = get_tags(tagged=tagged, tagged_for=tagged_for, tag_type=tag_type)
    return {'label':label,
            'tags' : tags,
            'tagged_class' : tagged.__class__.__name__,
            'tagged_id' : tagged.id,
            'tag_type' : tag_type}


@register.inclusion_tag('plus_tags/list_and_form.html')
def plus_tag(label, tag_type, tagged, tagged_for) :
    """XXX update to deal with tagged for and tagged by
    """

    if tagged.__class__ == TemplateSecureWrapper:
        tagged = tagged.obj()
    if tagged_for.__class__ == TemplateSecureWrapper:
        tagged_for == tagged_for.obj()
    if tagged_for == '' :
        tagged_for = None
    if tag_type == '' :
        tag_type = 'tag'
    tags = get_tags(tagged=tagged, tagged_for=tagged_for, tag_type=tag_type)

    return {'label':label,
            'tags' : tags, 
            'tagged_class' : tagged.__class__.__name__ ,
            'tagged_id' : tagged.id,
            'tag_type' : tag_type}


@register.inclusion_tag('plus_tags/goto_tag.html')
def goto_tag(search_domain=None):
    return {'search_domain':search_domain}
