try:
    set
except NameError:
    from sets import Set as set

from django import template
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse


register = template.Library()

DEFAULT_PAGINATION = getattr(settings, 'PAGINATION_DEFAULT_PAGINATION', 20)
DEFAULT_WINDOW = getattr(settings, 'PAGINATION_DEFAULT_WINDOW', 8)
DEFAULT_ORPHANS = getattr(settings, 'PAGINATION_DEFAULT_ORPHANS', 0)
INVALID_PAGE_RAISES_404 = getattr(settings, 'PAGINATION_INVALID_PAGE_RAISES_404',
    False)


def plus_paginate_header(context):
    try:
        paginator = context['paginator']
        page_obj = context['page_obj']        
        page_range = paginator.page_range
    except KeyError, AttributeError:
        return {}
    return {'page_obj': page_obj,
            'paginator_count': str(paginator.count),
            'start_index':str(page_obj.start_index()),
            'end_index': str(page_obj.end_index()),
            'page_range':page_range,
            'is_paginated': paginator.count > paginator.per_page,
            'search_terms':context['search_terms']}
register.inclusion_tag('pagination/paginate_header.html', takes_context=True)(plus_paginate_header)

def plus_paginate(context, listing_args, window=DEFAULT_WINDOW):
    """
    Renders the ``pagination/pagination.html`` template, resulting in a
    Digg-like display of the available pages, given the current page.  If there
    are too many pages to be displayed before and after the current page, then
    elipses will be used to indicate the undisplayed gap between page numbers.
    
    Requires one argument, ``context``, which should be a dictionary-like data
    structure and must contain the following keys:
    
    ``paginator``
        A ``Paginator`` or ``QuerySetPaginator`` object.
    
    ``page_obj``
        This should be the result of calling the page method on the 
        aforementioned ``Paginator`` or ``QuerySetPaginator`` object, given
        the current page.
    
    This same ``context`` dictionary-like data structure may also include:
    
    ``getvars``
        A dictionary of all of the **GET** parameters in the current request.
        This is useful to maintain certain types of state, even when requesting
        a different page.
        """
    
    try:
        paginator = context['paginator']
        page_obj = context['page_obj']
        page_range = paginator.page_range
        # First and last are simply the first *n* pages and the last *n* pages,
        # where *n* is the current window size.
        low = max(0, page_obj.number - window - 1)
        high = page_obj.number + window
        pages = set(page_range[low:high])
        if listing_args['tag_string']:
            if listing_args['group_id']:
                url = reverse(listing_args['tagged_url'], args=[listing_args['group_id'], listing_args['tag_string']])
            else:
                url = reverse(listing_args['tagged_url'], args=[listing_args['tag_string']])
        else:
            if listing_args['group_id']:            
                url = reverse(listing_args['search_url'], args=[listing_args['group_id']])
            else:
                url = reverse(listing_args['search_url'])

        # If there's no overlap between the current set of pages and the last
        # set of pages, then there's a possible need for elusion.

        to_return = {
            'pages': pages,
            'page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': paginator.count > paginator.per_page,
            'no_pages': page_obj.paginator.num_pages,
            'url':url
        }
        if 'request' in context:
            getvars = context['request'].GET.copy()
            if 'page' in getvars:
                del getvars['page']
            if len(getvars.keys()) > 0:
                to_return['getvars'] = "&%s" % getvars.urlencode()
            else:
                to_return['getvars'] = ''
        return to_return
    except KeyError, AttributeError:
        return {}
register.inclusion_tag('pagination/pagination.html', takes_context=True)(plus_paginate)
