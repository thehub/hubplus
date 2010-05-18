from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404 
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.encoding import smart_str
from django.db import transaction
from django.utils import simplejson

from apps.plus_groups.models import TgGroup
from django.core.urlresolvers import reverse

from django.template import defaultfilters

from apps.plus_feed.models import FeedItem 

from apps.plus_lib.models import DisplayStatus, add_edit_key
from apps.plus_lib.parse_json import json_view
from apps.plus_lib.search import side_search_args, listing_args
from apps.plus_permissions.models import SecurityTag, GenericReference
from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException, SecureWrapper, secure_wrap, TemplateSecureWrapper
from apps.plus_permissions.types.TgGroup import *

from django.contrib.auth.decorators import login_required


from apps.plus_groups.forms import TgGroupForm, TgGroupMemberInviteForm, AddContentForm, TgGroupMessageMemberForm

from apps.plus_permissions.api import secure_resource, site_context, has_access
from apps.plus_permissions.default_agents import get_anon_user, get_site, get_all_members_group

from apps.plus_permissions.proxy_hmac import hmac_proxy

from django.contrib.contenttypes.models import ContentType

from apps.plus_resources.models import get_permissioned_resources_for
import itertools


def subsearch(f) :
    """ decorator for filtered explorations of items in groups """
    def _subsearch(request, group, tag_string='', current_app='plus_groups',  
                   template_name='plus_explore/explore_filtered.html', **kwargs) :
        form=SearchForm(request.GET)
        if form.is_valid():
            search, order = set_search_order(request, form)
        else:
            # what should we do here?
            raise Exception('Search form is invalid')
        search_and_listing_args_dict = f(request, group, tag_string, search, order, current_app=current_app, **kwargs)
        return render_to_response(template_name, search_and_listing_args_dict, 
                                  context_instance=RequestContext(request, current_app=current_app))
    
    return _subsearch

@secure_resource(TgGroup, required_interfaces=['Viewer'], with_interfaces=['Viewer'])
@subsearch
def group_resources(request, group, tag_string, search, order, current_app, **kwargs):
    resource_listings_args = listing_args(current_app + ':group_resources', current_app + ':group_resources_tag', 
                                          tag_string=tag_string, search_terms=search, multitabbed=False, 
                                          order=order, template_base='plus_lib/listing_frag.html', 
                                          template_base_div_id='resources', group_id=group.id)
    search_types = narrow_search_types('Resource')
    results = plus_search(resource_listings_args['tag_filter'], search, search_types, order, in_group=group.get_ref())
    return {'search':results, 'listing_args':resource_listings_args}


def make_group_members(member_or_host, make_profile_id_list) :
    """ We want two copies of this view handler, one which is based on list of group members,
    other which is based on group hosts.
    """
    @secure_resource(TgGroup, required_interfaces=['Viewer'], with_interfaces=['Viewer'])
    @subsearch
    def group_members(request, group, tag_string, search, order, current_app, **kwargs):
        member_listings_args = listing_args(current_app + ':group_%s'%member_or_host, 
                                            current_app + ':group_%s_tag'%member_or_host, 
                                            tag_string=tag_string, search_terms=search, multitabbed=False, 
                                            order=order, template_base='plus_lib/listing_frag.html', 
                                            template_base_div_id=member_or_host, group_id=group.id)

        search_types = narrow_search_types('Profile')
        member_profile_ids=make_profile_id_list(group)
        results = plus_search(member_listings_args['tag_filter'], search, search_types, order, 
                              extra_filter={'id__in':member_profile_ids})

        return {'search':results, 'listing_args':member_listings_args}

    return group_members

group_members = make_group_members('members', lambda group : [x.get_profile().get_ref().id for x in group.users.all()])
group_hosts = make_group_members('hosts', 
                                 lambda group : [x.get_profile().get_ref().id for x in group.get_admin_group().users.all()])



def resources(group, tags=[], order=None, search=''):
    search_types = narrow_search_types('Resource')
    return plus_search(tags, search, search_types, order, in_group=group.get_ref())

def a_member_search(group, tags=[], order=None, search='', member_profile_ids=[]):
    search_types = narrow_search_types('Profile')
    return plus_search(tags, search, search_types, order, extra_filter={'id__in':member_profile_ids})

#@secure_resource(TgGroup, required_interfaces=['Viewer'], with_interfaces=['Viewer'])
# above is MUCH MUCH faster (whole request *10 faster), it shouldn't have to be this way
@secure_resource(TgGroup)
def group(request, group, template_name="plus_groups/group.html", current_app='plus_groups', **kwargs):

    if not group :
        raise Http404(_('There is no group with this id'))

    user = request.user

    can_join = False
    apply = False
    leave = False
    invite = False
    can_comment = False
    message = False
    add_link = False
    can_tag = False
    can_change_avatar = False
    has_accept = False
    can_delete = False


    editable_group_type = group.group_type != settings.GROUP_HUB_TYPE

    if user.is_authenticated():
        if user.is_direct_member_of(group.get_inner()):
            # can now leave group if you aren't the last one out
            if group.get_no_members() > 1 :
                leave = True
            try :
                group.invite_member
                invite = True
            except Exception, e :# user doesn't have invite permission
                pass

        else :
            try :
                group.join 
                can_join = True
            except Exception, e: # user doesn't have join permission
                pass
            try :
                if not can_join :
                    group.apply
                    apply = True
            except Exception, e : # user doesn't have apply permission
                pass

        try : 
            group.comment
            can_comment = True
            can_tag = True # XXX commentor interface governs who can tag. Do we need a special tag interface?
        except :
            pass


        try :
            group.message_members
            message = True
        except :
            pass
        
        try :
            group.create_Link
            add_link = True
        except Exception, e :
            print e
            pass

        try :
            group.change_avatar
            can_change_avatar  = True
        except Exception, e:
            pass

        try :
            dummy = group.delete
            can_delete = True
        except :
            pass

        if has_access(request.user, None, 'Application.Accept', group._inner.get_security_context()):
            has_accept = True
        else:
            has_accept = False
    
    tweets = FeedItem.feed_manager.get_from(group).order_by("-sent")     

    try:
        group.get_all_sliders
        perms_bool = True
    except PlusPermissionsNoAccessException:
        perms_bool = False

    if kwargs['type'] == 'hub':
        type_name = hub_name()
    else:
        type_name = "Group"

    search_types = narrow_search_types(type_name)
    side_search = side_search_args(current_app + ':groups', search_types[0][1][2])

    search = request.GET.get('search', '')
    order = request.GET.get('order', '')
    resource_search = resources(group=group, search=search, order=order)
    resource_listing_args = listing_args(current_app + ':group_resources', current_app + ':group_resources_tag', tag_string='', search_terms=search, multitabbed=False, order=order, template_base='plus_lib/listing_frag.html', search_type_label='resources')
    resource_listing_args['group_id'] = group.id

    ##############Here we should use the "plus_search" function from plus_explore as above########

    member_search = a_member_search(group=group, search=search, order=order, 
                                    member_profile_ids=[x.get_profile().get_ref().id for x in group.users.all()])
    host_search = a_member_search(group=group.get_admin_group(), search=search, order=order, 
                                  member_profile_ids=[x.get_profile().get_ref().id for x in group.get_admin_group().users.all()])
    member_listing_args = listing_args(current_app+':group_members', current_app+':group_members_tag', tag_string='', search_terms=search, multitabbed=False, order=order, template_base='plus_lib/listing_frag.html', search_type_label='members', group_id=group.id)

    host_listing_args = listing_args(current_app+':group_hosts', current_app+':group_hosts_tag', tag_string='', search_terms=search, multitabbed=False, order=order, template_base='plus_lib/listing_frag.html', search_type_label='hosts', group_id=group.id)
    member_count = group.users.all().count()
    host_count = group.get_admin_group().users.all().count()


    ##############################################################################################

    return render_to_response(template_name, {
            "head_title" : "%s" % group.get_display_name(),
            "status_type" : 'group',
            #"status_since" : status_since,
            "group" : TemplateSecureWrapper(group),
            "target_class" : ContentType.objects.get_for_model(group.get_inner()).id,
            "target_id" : group.get_inner().id,
            #"members" : members,
            "member_count" : member_count,
            "leave": leave,
            "can_join" : can_join, 
            "apply" : apply, 
            "invite" : invite, 
            "can_comment" : can_comment, 
            "message" : message,
            "add_link" : add_link,
            "can_tag" : can_tag,
            "can_change_avatar" : can_change_avatar,
            "can_delete" : can_delete, 
            #"hosts": hosts,
            "host_group_id":group.get_admin_group().id,
            "host_group_app_label":group.get_admin_group().group_app_label() + ':group',
            "is_host":user.is_admin_of(group.get_inner()),
            "host_count": host_count,
            "tweets" : tweets,
            "permissions": perms_bool,
            'side_search_args':side_search,
            'resource_search':resource_search,
            'resource_listing_args':resource_listing_args,
            'member_search':member_search,
            'member_listing_args':member_listing_args,
            'host_search':host_search,
            'host_listing_args':host_listing_args,
            'group_id':group.id,
            'search_types':search_types,
            'tagged_url':current_app + ':groups_tag',
            'has_accept':has_accept,
            'editable_group_type':editable_group_type,
            }, context_instance=RequestContext(request, current_app=current_app)
    )

from apps.plus_lib.utils import hub_name_plural, hub_name
from apps.plus_explore.views import plus_search, get_search_types, narrow_search_types, set_search_order
from apps.plus_explore.forms import SearchForm



@site_context
def groups(request, site, tag_string='', type='other', template_name='plus_explore/explore_filtered.html', current_app='plus_groups'):
    form = SearchForm(request.GET)
    if form.is_valid():
        search, order = set_search_order(request, form)
    else:
        search = ''
        search_type = ''

    create_group = False
    if request.user.is_authenticated():

        try:
            if current_app == 'groups':
                site.create_virtual
            else :
                site.create_hub
            create_group = True
        except Exception, e:
            print "User can't create a group",e
 
    if type == 'hub':
        head_title = _(hub_name_plural())
        type_name = hub_name()
    else:
        head_title = _('Groups')
        type_name = "Group"

    # hmm shouldn't we just use current app to determine search_types?        
    search_types = narrow_search_types(type_name) 
    side_search = side_search_args(current_app + ':groups', search_types[0][1][2])

    listing_args_dict = listing_args(current_app + ':groups', current_app + ':groups_tag', tag_string=tag_string, search_terms=search, multitabbed=False, order=order, template_base="site_base.html", search_type_label=head_title)
    search_dict = plus_search(listing_args_dict['tag_filter'], search, search_types, order)

    return render_to_response(template_name, 
                              {'head_title':head_title,
                               'search':search_dict,
                               'listing_args':listing_args_dict,
                               'search_args':side_search,
                               "create_group":create_group,
                               "obj_type": type_name,
                               'intro_box_override':True}, 
                             context_instance=RequestContext(request,
                                                             current_app=current_app,
                                                             ))





@login_required
@secure_resource(TgGroup, required_interfaces=['Join','Viewer'])
def join(request, group,  template_name="plus_groups/group.html", current_app='plus_groups', **kwargs):
    group.join(request.user)
    return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id,)))


from apps.plus_contacts.status_codes import PENDING

@secure_resource(TgGroup, required_interfaces=['Viewer'])
def apply(request, group, current_app='plus_groups', **kwargs):
    if request.user == get_anon_user():
        return HttpResponseRedirect(reverse('acct_apply'))
    if Application.objects.filter(status=PENDING, group=group, applicant_object_id=request.user.id, applicant_content_type=ContentType.objects.get_for_model(User)).count():
        request.user.message_set.create(message=_("You have already have a pending application to %(group_name)s.") % {'group_name': group.get_display_name()})        
    else:
        group.apply(request.user, request.user) # add reason for applying form here
        request.user.message_set.create(message=_("Application to %(group_name)s sent.") % {'group_name': group.get_display_name()})

    return HttpResponseRedirect(reverse(current_app + ':group', args=(group.id,)))            
    

@login_required
@secure_resource(TgGroup, required_interfaces=['Invite', 'Viewer'])
def invite(request, group, template_name='plus_groups/invite.html', current_app='plus_groups', **kwargs):
    if request.user == get_anon_user():
        return HttpResponseRedirect(reverse('acct_invite'))

    if request.POST :
        form = TgGroupMemberInviteForm(request.POST)
        if form.is_valid() :
            invited = form.cleaned_data['invited']
            from apps.plus_groups.models import invite_to_group
            invite_to_group(group,invited,request.user,form.cleaned_data['special_message'])
            message = _("You have invited %(invited)s to %(group)s.") % {'invited':invited,'group':group.get_display_name()}
            request.user.message_set.create(message=message)

            return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id,)))
            
    else :
        form = TgGroupMemberInviteForm()
    return render_to_response(template_name,{
            'form' : form,
            'group' : group,
            'group_id' : group.id,
            }, context_instance=RequestContext(request, current_app=current_app))



@login_required
@secure_resource(TgGroup, required_interfaces=['Viewer']) 
def leave(request, group, template_name="plus_groups/group.html", current_app='plus_groups', **kwargs):
    group.leave(request.user)
    return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id,)))



@hmac_proxy
@secure_resource(TgGroup,["ManageMembers"])
def add_member(request, group, username, current_app='plus_groups', **kwargs) :
    user = get_object_or_404(User, username=username)
    group.add_member(user)
    return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id,)))


@login_required
@secure_resource(TgGroup, required_interfaces=['Message','Viewer'])
def message_members(request, group, current_app='plus_groups', **kwargs) :
    template_name = "plus_groups/message_members.html"
    if request.POST :
        form = TgGroupMessageMemberForm(request.POST)
        if form.is_valid() :
            group.message_members(request.user, form.data['message_header'], form.data['message_body'])
            message = _("You have successfully messaged everyone in %(group_name)s") % {'group_name':group.get_display_name()}
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id,)))
    else :
        form = TgGroupMessageMemberForm()
    return render_to_response(template_name, 
                              {'form' : form,
                               'group': group,
                               'group_id': group.id}, context_instance=RequestContext(request, current_app=current_app))


from apps.synced import synced_transaction
@synced_transaction
@login_required
@site_context
def create_group(request, site, template_name="plus_groups/create_group.html", current_app='plus_groups', **kwargs):

    if request.POST :
        form = TgGroupForm(request.POST)

        if not form.is_valid() :
            print form.errors
        else :
            group = form.save(request.user, site)
            return HttpResponseRedirect(reverse(current_app + ':group', args=(group.id,)))
    else :
        form = TgGroupForm()
    
    if current_app == 'groups' :
        name_of_created = "Group"
        is_hub = False
    else :
        name_of_created = hub_name()
        is_hub = True

    return render_to_response(template_name, {
            "head_title" : "Create New %s"%name_of_created,
            "name_of_created": name_of_created,
            "head_title_status" : "",
            "group" : form,
            "form" : form,
            "is_hub" : is_hub, 
            }, context_instance=RequestContext(request, current_app=current_app))


@login_required
@secure_resource(TgGroup)
def group_field(request, group, classname, fieldname, *args, **kwargs) :
    """ Get the value of one field from the group, so we can write an ajaxy editor """
    return one_model_field(request, p, fieldname, kwargs.get('default', ''), TgGroupForm)


@login_required
@secure_resource(obj_schema={'group':[TgGroup]})
def add_content_object(request, group, current_app='plus_groups', **kwargs):
    form_args = request.POST.copy()
    form_args['current_app'] = current_app
    form = AddContentForm(form_args)
    if form.is_valid():
        title = form.cleaned_data['title']
        type_string = form.cleaned_data['type_string']
        create = getattr(group, "create_" + type_string)
        title = form.cleaned_data['title']
        name = form.cleaned_data['name']
        cls = ContentType.objects.get(model=form.cleaned_data['type_string'].lower()).model_class()
        try:
            #if a stub exists, use it
            obj = cls.objects.plus_get(request.user, name=form.cleaned_data['name'], in_agent=group.get_ref(), stub=True)
        except cls.DoesNotExist:
            obj = create(request.user, title=title, name=name, in_agent=group.get_ref(), stub=True)
            obj.save()

        #can't do a normal redirect via ajax call, so tell the js to redirect for us

        return HttpResponse('redirect:' + reverse(current_app + ':edit_' + type_string, args=[group.id, obj.name]))
        
        #redirect to the edit page
        #return HttpResponseRedirect(reverse('edit_' + type_string, args=[group.id, obj.name]))
    
    return add_content_form(request, group.id, form)

 
def possible_create_interfaces():
    """return tuples of form, interface string, label, subtext
    """
    return [["CreateWikiPage", _("Page"), _("Create new wiki page")], 
            ["CreateResource", _("Upload"), _("Share a document")],
            ["CreateNews", _("News"), _("Create a new posting")],
            ["CreateEvent", _("Events"), _("Create a new event")]]


@login_required
@secure_resource(TgGroup)
def add_content_form(request, group, form=None, current_app='plus_groups', **kwargs):

    possible_interfaces = possible_create_interfaces()
    if group:
        _interfaces = [g.split('.')[1] for g in group._interfaces]
    else:
        _interfaces = []
    can_add = 0
    for iface in possible_interfaces:
        if iface[0] in _interfaces:
            iface.append(True)
            can_add += 1
        else:
            iface.append(False)
    return render_to_response("plus_groups/add_content.html", {'group':group, 'possible_interfaces': possible_interfaces, 'can_add':can_add, 'form':form}, RequestContext(request, current_app=current_app))



@json_view
def autocomplete(request, j=None, current_app='plus_groups', **kwargs):
    """filter groups to see which ones this user can add content too. Check that the user can create at least something on the groups that we autocomplete for them
    """
    user = request.user
    q = request.GET['q']
    limit = request.GET['limit']  
    groups = TgGroup.objects.plus_filter(user, interface_names=['Viewer', 'CreateWikiPage','CreateResource'], required_interfaces=['CreateWikiPage','CreateResource'], all_or_any='ANY', display_name__istartswith=q, level__in=['host', 'member'], limit=6)

    options = [{'display_name':group.display_name, 'id':str(group.id), 'interfaces':[iface.split('.')[1] for iface in group._interfaces]} for group in groups]
    return options


@json_view
def group_type_ajax(request,**kwargs) :
    return settings.GROUP_TYPES[0:-1] # miss off the last, because it's the Hub type


@json_view
def ajax_hub_list(request, username=None, **kwargs) :    
    if username :
       return [(t.id, t.display_name) for t in User.objects.plus_get(request.user, username=username).hubs()]
    else : 
       return [(t.id, t.display_name) for t in TgGroup.objects.hubs()]



@login_required
@secure_resource(TgGroup)
def delete(request, group, current_app='plus_groups', **kwargs) :
    if request.POST :
        # we're deleting
        if request.POST.has_key('delete_check') :
            group.delete()
        
        return HttpResponseRedirect(reverse(current_app + ':groups'))
    else :
        pass
    return render_to_response("plus_groups/delete_confirmation.html",
                              {
                               'group': group,
                               'group_name':group.get_inner().get_display_name(),
                               'group_id': group.id}, context_instance=RequestContext(request, current_app=current_app))

