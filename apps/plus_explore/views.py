from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from apps.plus_tags.models import top_tags, get_resources_for_tag_intersection, get_intersecting_tags
from apps.plus_groups.models import TgGroup
from django.core.urlresolvers import reverse

def index(request, template_name="plus_explore/explore.html"):
    if request.GET.get('search', ''):
        return filter(request, tag_string='')
    
    return render_to_response(template_name, {'head_title':_('Explore'), 'tags':top_tags()}, context_instance=RequestContext(request))

def get_virtual_groups():
    return TgGroup.objects.filter(place__name='HubPlus')

def get_search_types():
    v_groups = get_virtual_groups()
    #('All', (None, None, _('All')))
    return (('Profile', ({'content_type__model':'profile'}, None, _('Members'))), 
            ('Group', ({'content_type__model':'tggroup', 'object_id__in':v_groups}, None, _('Groups'))), 
            ('Hub',({'content_type__model':'tggroup'}, {'object_id__in':v_groups}, _('Hubs'))), 
            ('Resource', ({'content_type__model__in':['resource', 'wikipage']}, None, _('Resources'))), 
            )

def goto_tag(request):
    tag_string = request.GET.get('tag', '')
    if tag_string:
        return HttpResponseRedirect(reverse('explore_filtered', args=[tag_string]))
    return HttpResponseRedirect(reverse('explore'))

def filter(request, tag_string, template_name='plus_explore/explore_filtered.html'):
    """ this should be integrated with index into a single method - probably
    """
    tags = tag_string.split('+')
    search = request.GET.get('search', '')
    order = request.GET.get('order', '')
    explicit_order = ''
    if order:
        explicit_order = order
    items = {'All':[]}
    tag_intersection = []
    try:
        tags.remove('')
    except ValueError:
        pass
    if len(tags):
        items = {'All':get_resources_for_tag_intersection(tags)} #.order_by(order)}
        tag_intersection = get_intersecting_tags(items['All'], n=15)    

    search_types = get_search_types()
    all_items = items.get('All', [])
    if all_items:
        #split the results by type
        for typ_name, typ_filter in search_types:
            if typ_filter[0]:
                items[typ_name] = items['All'].filter(**typ_filter[0])
            if typ_filter[1]:
                if items.has_key(typ_name):
                    items[typ_name] = items[typ_name].exclude(**typ_filter[1])
                else:
                    items[typ_name] = items['All'].exclude(**typ_filter[1])
    # elif not tag_string:
    #     return render_to_response(template_name, {'head_title':_('Explore'), 'tags':top_tags()}, context_instance=RequestContext(request))
        
        
    search_types = [(typ, data[2], items[typ]) for typ, data in search_types if typ in items]
    if tag_string:
        search_type = 'explore_filtered'
    else:
        search_type = 'explore'
    return render_to_response(template_name, {'head_title':_('Explore'), 
                                              'order':order,
                                              'explicit_order':order,
                                              'search_terms':search,
                                              'items':all_items, 
                                              'tag_filter':tags,
                                              'tag_string':tag_string,
                                              'multiple_tags':len(tags)>1,
                                              'tag_intersection':tag_intersection,
                                              'search_types':search_types,
                                              'search_type':search_type}, context_instance=RequestContext(request))
