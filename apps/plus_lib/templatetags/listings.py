from django import template
register = template.Library()
from django.utils.http import urlquote


@register.inclusion_tag('plus_lib/tag_and_search.html')
def tag_and_search(tag_filter, multiple_tags, search_terms, tag_intersection, order=''):
    tag_string = '+'.join(tag_filter)

    tag_extra = []
    if order:
        tag_extra.append('order=' + order)
    if search_terms:
        tag_extra.append('search=' + search_terms)
    tag_extra = '&'.join(tag_extra)
    if tag_extra:
        tag_extra = '?' + tag_extra

    remove_tag_links = []
    for tag in tag_filter:
        tag_filter = tag_string.split('+')
        tag_filter.remove(tag)
        remove_tag_links.append((tag, '+'.join(tag_filter)))

    for tag in tag_intersection:
        tag['tag_filter'] = tag_string + '+' + tag['keyword']

    return {'tag_filter':tag_filter,
            'remove_tag_links':remove_tag_links,
            'multiple_tags':multiple_tags,
            'search_terms':search_terms,
            'tag_intersection':tag_intersection,
            'tag_extra':tag_extra}


@register.inclusion_tag('plus_lib/listing.html', takes_context=True)
def listing(context, items, results_label, order):
    return {'items':items,
            'results_label':results_label,
            'order':order,
            'request':context['request'],
            'search_terms':context['search_terms']
            }
    
