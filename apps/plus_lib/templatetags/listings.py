from django import template
register = template.Library()
from django.utils.http import urlquote
from apps.plus_lib.utils import search_caption_from_path

@register.inclusion_tag('plus_lib/tag_and_search.html',takes_context=True)
def tag_and_search(context, listing_args, tag_intersection):
    tag_extra = []
    if listing_args['order']:
        tag_extra.append('order=' + listing_args['order'])
    if listing_args['search_terms']:
        tag_extra.append('search=' + listing_args['search_terms'])
    tag_extra = '&'.join(tag_extra)
    if tag_extra:
        tag_extra = '?' + tag_extra

    remove_tag_links = []
    for tag in listing_args['tag_filter']:
        tag_tmp_filter = listing_args['tag_string'].split('+')
        tag_tmp_filter.remove(tag)
        remove_tag_links.append((tag, '+'.join(tag_tmp_filter)))

    for tag in tag_intersection:
        tag['tag_filter'] = listing_args['tag_filter'] + [tag['keyword']]
        tag['tag_filter'] = '+'.join(tag['tag_filter'])
    
    path = context['request'].path
    search_caption = search_caption_from_path(path)

    return {'listing_args':listing_args,
            'remove_tag_links':remove_tag_links,
            'tag_intersection':tag_intersection,
            'tag_extra':tag_extra,
            'search_caption':search_caption}


@register.inclusion_tag('plus_lib/listing.html', takes_context=True)
def listing(context, items, results_label, order, search_terms, listing_args):

    return {'items':items,
            'results_label':results_label,
            'order':order,
            'request':context['request'],
            'search_terms':search_terms,
            'listing_args':listing_args
            }
    

@register.inclusion_tag('plus_explore/side_search.html')
def side_search(search_args):
    return {'search_type':search_args['search_type'], 'search_type_label':search_args['search_type_label']}
    

@register.inclusion_tag('plus_explore/explore_filtered.html', takes_context=True)
def included_listing(context, search, listing_args):
    return {'search':search, 'listing_args':listing_args, 'request':context['request']}
