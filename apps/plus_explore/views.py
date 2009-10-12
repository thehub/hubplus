from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from apps.plus_tags.models import top_tags, get_resources_for_tag_intersection, get_intersecting_tags
from apps.plus_groups.models import TgGroup
from django.core.urlresolvers import reverse
from haystack.query import RelatedSearchQuerySet, EmptySearchQuerySet
from apps.plus_permissions.models import GenericReference
from django.db.models import Q
import settings

def index(request, template_name="plus_explore/explore.html"):
    if request.GET.get('search', ''):
        return filter(request, tag_string='')
    
    return render_to_response(template_name, {'head_title':_('Explore'), 'tags':top_tags()}, context_instance=RequestContext(request))

def get_virtual_groups():
    return TgGroup.objects.filter(place__name='HubPlus')

from plus_lib.utils import hub_name, hub_name_plural

def get_search_types():
    v_groups = get_virtual_groups()
    #('All', (None, None, _('All')))
    return (('Profile', ({'content_type__model':'profile'}, None, _('Members'))), 
            ('Group', ({'content_type__model':'tggroup', 'object_id__in':v_groups}, None, _('Groups'))), 
            (hub_name(),({'content_type__model':'tggroup'}, {'object_id__in':v_groups}, _(hub_name_plural()))), 
            ('Resource', ({'content_type__model__in':['resource', 'wikipage']}, None, _('Resources'))), 
            )

def goto_tag(request):
    tag_string = request.GET.get('tag', '')
    if tag_string:
        return HttpResponseRedirect(reverse('explore_filtered', args=[tag_string]))
    return HttpResponseRedirect(reverse('explore'))




# XXX pagination - separated per tab


def filter(request, tag_string, template_name='plus_explore/explore_filtered.html'):
    """ this should be integrated with index into a single method - probably
    """
    tags = tag_string.split('+')
    search = request.GET.get('search', '')
    order = request.GET.get('order', '')
    explicit_order = ''
    if order:
        explicit_order = order

    try:
        tags.remove('')
    except ValueError:
        pass
    
    all_results, search_types, tag_intersection  = plus_search(tags, search, get_search_types(), order)

    if tag_string:
        search_type = 'explore_filtered'
    else:
        search_type = 'explore'
    
    return render_to_response(template_name, {'head_title':_('Explore'), 
                                              'order':order,
                                              'explicit_order':order,
                                              'search_terms':search,
                                              'items': all_results,
                                              'items_len': len(all_results),
                                              'tag_filter':tags,
                                              'tag_string':tag_string,
                                              'multiple_tags':len(tags)>1,
                                              'tag_intersection':tag_intersection,
                                              'search_types':search_types,
                                              'search_type':search_type,
                                              'multitabbed':True,
                                              'results_label':'items',
                                              'base':"site_base.html"}, context_instance=RequestContext(request))

def plus_search(tags, search, search_types, order, extra_filter=None):
    items = get_resources_for_tag_intersection(tags)
    q = None
    for typ, info in search_types:
        if info[0]:
            typ_items = Q(**info[0])
            if info[1]:
                typ_items = typ_items & ~Q(**info[1])
        elif info[1]:
            typ_items = ~Q(**info[1])
        if not q:
            q = typ_items
        else:
            q = q | typ_items
    if extra_filter:
        q = q & Q(**extra_filter)
    if q:
        items = items.filter(q)
    
    results_map = {}
    tag_intersection = []
    if search:
        results = RelatedSearchQuerySet().auto_query(search)
        results_map = {}
        if results:
            all_results = results.load_all()
            all_results = all_results.load_all_queryset(GenericReference, items)
            results_map['All'] = [item.object for item in all_results]   #we really really shouldn't do this                
        else:
            results_map = {'All':EmptySearchQuerySet()}
    else:
        if items:
            results_map['All'] = items.all()

    if 'All' in results_map:
        tag_intersection = get_intersecting_tags(results_map['All'], n=15)    
        if len(search_types) > 1:
            for typ, info in search_types:
                if info[0]:
                    typ_items = items.filter(**info[0])
                    if info[1]:
                        typ_items = typ_items.exclude(**info[1])
                elif info[1]:
                    typ_items = items.exclude(**info[1])
                if search and results:
                    typ_items = all_results.load_all_queryset(GenericReference, typ_items)
                    typ_items = [item.object for item in typ_items] #we really really shouldn't do this
                    results_map[typ] = typ_items
    else:
        results_map = {'All':EmptySearchQuerySet()}

    search_types = [(typ, data[2], results_map[typ], len(results_map[typ])) for typ, data in search_types if results_map.has_key(typ)]
    return (results_map['All'], search_types, tag_intersection)
