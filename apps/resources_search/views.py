from apps.plus_explore.forms import SearchForm
from apps.plus_explore.views import plus_search, get_search_types, set_search_order
from apps.plus_lib.search import side_search_args, listing_args
from apps.plus_permissions.api import secure_resource, site_context
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template import RequestContext

def narrow_search_types(type_name):
    types = dict(get_search_types())
    return ((type_name, types[type_name]),)

@site_context
def resources(request, site, tag_string='', type='other', template_name='plus_explore/explore_filtered.html', current_app='plus_groups'):
    form = SearchForm(request.GET)
    if form.is_valid():
        search, order = set_search_order(request, form)
    else:
        search = ''
        search_type = ''
 

    head_title = _('Resources')
    type_name = "Resource"

    # hmm shouldn't we just use current app to determine search_types?        
    search_types = narrow_search_types(type_name) 
    side_search = side_search_args('resources', search_types[0][1][2])

    listing_args_dict = listing_args('resources', 'resources_tag', tag_string=tag_string, search_terms=search, multitabbed=False, order=order, template_base="site_base.html", search_type_label=head_title)
    search_dict = plus_search(listing_args_dict['tag_filter'], search, search_types, order)
    
    return render_to_response(template_name, 
                              {'head_title':head_title,
                               'search':search_dict,
                               'listing_args':listing_args_dict,
                               'search_args':side_search,
                               "obj_type": type_name,
                               'intro_box_override':True}, 
                              context_instance=RequestContext(request,
                                                              current_app=current_app))
