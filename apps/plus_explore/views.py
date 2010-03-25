from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from apps.plus_tags.models import get_resources_for_tag_intersection, get_intersecting_tags, scale_tag_weights
from apps.plus_groups.models import TgGroup
from apps.profiles.models import Profile
from django.core.urlresolvers import reverse
from haystack.query import RelatedSearchQuerySet, EmptySearchQuerySet
from apps.plus_permissions.models import GenericReference
from apps.plus_wiki.models import WikiPage
from apps.plus_resources.models import Resource
from apps.plus_lib.search import side_search_args, listing_args


from django.db.models import Q
import settings
from apps.plus_explore.forms import SearchForm

def index(request, template_name="plus_explore/explore.html"):
    form = SearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search', '')
        search_type = form.cleaned_data.get('current_area', '')
        if search_type:
            url = reverse(search_type)
            if search:
                url += '?search=' + search
            return HttpResponseRedirect(url)

        if search:
            return filter(request, tag_string='')
    else:
        pass
    
    side_search = side_search_args('', '')
    
    return render_to_response(template_name, 
                              {'head_title':settings.EXPLORE_NAME, 
                               'search_args':side_search,
                               'intro_box_override':True}, context_instance=RequestContext(request))     




from apps.plus_lib.utils import hub_name, hub_name_plural

def get_search_types():
    v_groups = TgGroup.objects.virtual()
    hubs = TgGroup.objects.hubs()
    #('All', (None, None, _('All')))
    return (('Profile', ({'content_type__model':'profile'}, None, _('Members'))), 
            ('Group', ({'content_type__model':'tggroup', 'object_id__in':v_groups}, None, _('Groups'))), 
            #(hub_name(),({'content_type__model':'tggroup'}, {'object_id__in':v_groups}, _(hub_name_plural()))), 
            (hub_name(),({'content_type__model':'tggroup','object_id__in':hubs},None,_(hub_name_plural()))),
            ('Resource', ({'content_type__model__in':['resource', 'wikipage']}, None, _('Resources'))), 
            )


def narrow_search_types(type_name):
    types = dict(get_search_types())
    return ((type_name, types[type_name]),)



def goto_tag(request):
    tag_string = request.GET.get('tag', '')
    if tag_string:
        return HttpResponseRedirect(reverse('explore_filtered', args=[tag_string]))
    return HttpResponseRedirect(reverse('explore'))

# XXX pagination - separated per tab



def set_search_order(request, form):
    search = form.cleaned_data.get('search', '')
    order = form.cleaned_data.get('order', '')
    if not order:
        order = request.session.get('order', 'modified')

    was_search = request.session.get('was_search', False)
    if search:
        if not was_search:
            order = 'relevance'
            request.session['was_search'] = True
            HttpResponseRedirect(request.path + '?order=' + order + '&search=' + search)
        request.session['was_search'] = True
    else:
        if was_search:
            order = 'modified'
            request.session['was_search'] = False
            HttpResponseRedirect(request.path + '?order=' + order)
        request.session['was_search'] = False

    request.session['order'] = order 
    return search, order

def filter(request, tag_string, template_name='plus_explore/explore_filtered.html'):
    """ this should be integrated with index into a single method - probably
    """
    form = SearchForm(request.GET)
    if form.is_valid():
        search, order = set_search_order(request, form)
    else:
        search = ''
        order = ''

    side_search = side_search_args('', '')
    search_types = get_search_types()
    head_title = settings.EXPLORE_NAME
    listing_args_dict = listing_args('explore', 'explore_filtered', tag_string=tag_string, search_terms=search, multitabbed=True, order=order, template_base="site_base.html", search_type_label=head_title)
    search_dict = plus_search(listing_args_dict['tag_filter'], search, search_types, order)
    
    return render_to_response(template_name, {'head_title':head_title, 
                                              'listing_args':listing_args_dict,
                                              'search':search_dict,
                                              'search_args':side_search,}, context_instance=RequestContext(request))


object_type_filters = {Resource:{'stub':False},
                       WikiPage:{'stub':False},
                       Profile:{'user__active':True},
                       TgGroup:{}}

def plus_search(tags, search, search_types, order=None, in_group=None, extra_filter=None):
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

    included = None
    for obj_class, included_filter in object_type_filters.items():
        objs = obj_class.objects.filter(**included_filter)
        included_search = {'content_type__model':obj_class.__name__.lower(),
                           'object_id__in':objs}
        
        if not included:
            included = Q(**included_search)
        included = included | Q(**included_search)

    items = items.filter(included)

    if in_group:
        # this should be implemented using the code just above and an external search filter arg
        page_ids = WikiPage.objects.filter(in_agent=in_group, stub=False)
        wikipages = Q(**{'content_type__model':'wikipage',
                         'object_id__in':page_ids})
        resource_ids = Resource.objects.filter(in_agent=in_group, stub=False)
        resources = Q(**{'content_type__model':'resource',
                         'object_id__in':resource_ids})

        q = resources | wikipages
        items = items.filter(q)
 
    results_map = {}
    tag_intersection = []
    if search:
        results = RelatedSearchQuerySet().auto_query(search)
        results_map = {}
        if results:
            all_results = results.load_all_queryset(GenericReference, items)
            if order == 'relevance':
                all_results = all_results.load_all()  # this bit is quite evil and makes things really inefficient for large searches
                                              # a better approach would be to get all the ids directly from the fulltext index and use them as a filter for GenericReferences 
                results_map['All'] = [item.object for item in all_results]   #we really really shouldn't do this 
                items_len = len(results_map['All'])
            else:
                search_results = [result.pk for result in all_results]
                results_map['All'] = items.filter(id__in=search_results).order_by(order)
                items_len = results_map['All'].count()
        else:
            results_map = {'All':EmptySearchQuerySet()}
            items_len = 0
    else:
        if items:
            items = items.order_by('creator')
            items_len = items.count()
            results_map['All'] = items
        else:
            items_len = 0
            results_map = {'All':EmptySearchQuerySet()}            

    if order == 'modified':
        results_map['All'] = results_map['All'].order_by('-' + order)
    elif order == 'display_name':
        results_map['All'] = results_map['All'].order_by(order)        

    if 'All' in results_map:
        tag_intersection = get_intersecting_tags(results_map['All'], n=15)

        if len(search_types) > 1:
            for typ, info in search_types:
                if info[0]:
                    typ_items = items.filter(**info[0])
                if info[1]:
                    typ_items = items.exclude(**info[1])
                if search and results and order == 'relevance':
                        # why do this again when we could just separate results using python
                        typ_items = all_results.load_all_queryset(GenericReference, typ_items)
                        typ_items = [item.object for item in typ_items] #we really really shouldn't do this
                if typ_items:
                    results_map[typ] = typ_items
    else:
        results_map = {'All':EmptySearchQuerySet()}

    search_type_data = []
    for typ, data in search_types:
        if results_map.has_key(typ):
            try:
                type_len = results_map[typ].count()
            except TypeError:
                type_len = len(results_map[typ])
            
            search_type_data.append((typ, data[2], results_map[typ], type_len))

    return {'All':results_map['All'], 'items_len':items_len, 'search_types':search_type_data, 'tag_intersection':tag_intersection}


