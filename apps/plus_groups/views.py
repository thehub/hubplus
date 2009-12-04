from django.shortcuts import render_to_response, get_object_or_404
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

from microblogging.models import Tweet, TweetInstance, Following

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




#separate params for searches

@secure_resource(TgGroup)
def group_resources(request, group, tag_string='', template_name='plus_explore/explore_filtered.html', current_app='plus_groups', **kwargs):
    tags = tag_string.split('+')
    search = request.GET.get('search', '')
    order = request.GET.get('order', '')

    resource_listing_args = listing_args(current_app + ':group_resources', current_app + ':group_resources_tag', tag_string=tag_string, search_terms=search, multitabbed=False, order=order, template_base='plus_lib/listing_frag.html')
    resource_listing_args['group_id'] = group.id
    resources_dict = resources(group, resource_listing_args['tag_filter'], order, search)

    return render_to_response(template_name, {'search':resources_dict,
                                              'listing_args':resource_listing_args}, context_instance=RequestContext(request, current_app=current_app))





def resources(group, tags=[], order=None, search=''):
    search_types = narrow_search_types('Resource')
    return plus_search(tags, search, search_types, order, in_group=group.get_ref())


@secure_resource(TgGroup)
def group(request, group, template_name="plus_groups/group.html", current_app='plus_groups', **kwargs):

    user = request.user
    if not user.is_authenticated():
        user = get_anon_user()
        request.user = user 
            
    members = group.get_users()[:10]
    member_count = group.get_no_members()

    hosts = group.get_admin_group().get_users()[:10]
    host_count = group.get_admin_group().get_no_members()

    can_join = False
    apply = False
    leave = False
    invite = False
    can_comment = False
    message = False
    add_link = False
    can_tag = False
    can_change_avatar = False

    if user.is_authenticated():
        if user.is_direct_member_of(group.get_inner()):
            if not user.is_admin_of(group.get_inner()) or group.get_inner().get_admin_group() == group.get_inner():
                # can't leave a group you're the admin of *unless* the group is its own admin
                # (without the second clause, you'd be trapped there forever)
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
        
        if has_access(request.user, None, 'Application.Accept', group._inner.get_security_context()):
            has_accept = True
        else:
            has_accept = False

    tweets = TweetInstance.objects.tweets_from(group).order_by("-sent") 
    if tweets :
        latest_status = tweets[0]
        dummy_status = DisplayStatus(
            defaultfilters.safe( defaultfilters.urlize(latest_status.html())),
                                 defaultfilters.timesince(latest_status.sent) )
    else:
        dummy_status = DisplayStatus('No status', '')

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

    return render_to_response(template_name, {
            "head_title" : "%s" % group.get_display_name(),
            "head_title_status" : dummy_status,
            "group" : TemplateSecureWrapper(group),
            "target_class" : ContentType.objects.get_for_model(group.get_inner()).id,
            "target_id" : group.get_inner().id,
            "members" : members,
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
            "hosts": hosts,
            "host_count": host_count,
            "tweets" : tweets,
            "permissions": perms_bool,
            'side_search_args':side_search,
            'resource_search':resource_search,
            'resource_listing_args':resource_listing_args,
            'group_id':group.id,
            'search_types':search_types,
            'tagged_url':current_app + ':groups_tag',
            'has_accept':has_accept
            }, context_instance=RequestContext(request, current_app=current_app)
    )

from apps.plus_lib.utils import hub_name_plural, hub_name
from apps.plus_explore.views import plus_search, get_search_types
from apps.plus_explore.forms import SearchForm

def narrow_search_types(type_name):
    types = dict(get_search_types())
    return ((type_name, types[type_name]),)

@site_context
def groups(request, site, tag_string='', type='other', template_name='plus_explore/explore_filtered.html', current_app='plus_groups'):
    form = SearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search', '')
        order = form.cleaned_data.get('order', '')
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
@secure_resource(TgGroup, required_interfaces=['Viewer']) 
def leave(request, group, template_name="plus_groups/group.html", current_app='plus_groups', **kwargs):
    group.leave(request.user)
    return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id,)))

@login_required
@secure_resource(TgGroup, required_interfaces=['Invite', 'Viewer'])
def invite(request, group, template_name='plus_groups/invite.html', current_app='plus_groups', **kwargs):

    if request.POST :
        form = TgGroupMemberInviteForm(request.POST)
        if form.is_valid() :
            invited = form.cleaned_data['user']
            group.invite_member(invited, form.cleaned_data['special_message'], request.user, request.get_host())
            return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id,)))
            
    else :
        form = TgGroupMemberInviteForm()
    return render_to_response(template_name,{
            'form' : form,
            'group' : group,
            'group_id' : group.id,
            }, context_instance=RequestContext(request, current_app=current_app))


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
            group.message_members(request.user, form.data['message_header'], form.data['message_body'], request.get_host())
            message = _("You have successfully messaged everyone in %(group_name)s") % {'group_name':group.get_display_name()}
            request.user.message_set.create(message=message)
            return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id,)))
    else :
        form = TgGroupMessageMemberForm()
    return render_to_response(template_name, 
                              {'form' : form,
                               'group': group,
                               'group_id': group.id}, context_instance=RequestContext(request, current_app=current_app))


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

