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

from apps.plus_groups.models import TgGroup, name_from_title
from django.core.urlresolvers import reverse

from django.template import defaultfilters

from microblogging.models import Tweet, TweetInstance, Following

from apps.plus_lib.models import DisplayStatus, add_edit_key
from apps.plus_lib.parse_json import json_view
from apps.plus_permissions.models import SecurityTag, GenericReference
from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException, SecureWrapper, secure_wrap, TemplateSecureWrapper
from apps.plus_permissions.types.TgGroup import *
from django.contrib.auth.decorators import login_required

from apps.plus_groups.forms import TgGroupForm, TgGroupMemberInviteForm, AddContentForm, TgGroupMessageMemberForm

from apps.plus_permissions.api import secure_resource, site_context
from apps.plus_permissions.default_agents import get_anon_user, get_site

from apps.plus_permissions.proxy_hmac import hmac_proxy

from django.contrib.contenttypes.models import ContentType

from apps.plus_resources.models import get_permissioned_resources_for
import itertools


#XXX Temporarily here. If this becomes a long term way of listing wiki pages for groups' 
# this should be moved into plus_wiki app
def get_pages_for(group) :
    content_type = ContentType.objects.get_for_model(group)
    return WikiPage.objects.filter(in_agent__content_type=content_type, in_agent__object_id=group.id)

def get_resources_and_pages_for(user, group):
    #objects = GenericReference.objects.filter(object_id=group.get_ref().id, content_type)
    objects = []
    q1 = get_pages_for(group)
    q2 = get_permissioned_resources_for(user, group)
    for thing in itertools.chain(q1,q2):
        objects.append(thing) 
    return objects

@secure_resource(TgGroup)
def group(request, group, template_name="plus_groups/group.html", current_app='plus_groups', **kwargs):

    user = request.user
    if not user.is_authenticated():
        user = get_anon_user()
        request.user = user 
        
    search_terms = request.GET.get('search_terms', '')
    
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

    if user.is_authenticated():
        if user.is_direct_member_of(group.get_inner()):
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
        except :
            pass


        try :
            group.message
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
            group.description = group.description 
            # XXX dumb test for editor interface, need a Tag type in plus_permissions so this can be handled 
            can_tag = True
        except :
            pass
            

    tweets = TweetInstance.objects.tweets_from(group).order_by("-sent") 
    if tweets :
        latest_status = tweets[0]
        dummy_status = DisplayStatus(
            defaultfilters.safe( defaultfilters.urlize(latest_status.html())),
                                 defaultfilters.timesince(latest_status.sent) )
    else :
        dummy_status = DisplayStatus('No status', '')

    try:
        group.get_all_sliders
        perms_bool = True
    except PlusPermissionsNoAccessException:
        perms_bool = False
        
    # XXX replace when we slot permissions in
    # XXX replace when we have more sophisticated listings search
    #pages = get_pages_for(group.get_inner())
    #resources = get_resources_for(group.get_inner())
    
    objects = get_resources_and_pages_for(user, group)

    context = RequestContext(request, current_app=current_app)
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
            "hosts": hosts,
            "host_count": host_count,
            "tweets" : tweets,
            "permissions": perms_bool,
            "objects":objects,
            "search_type":"plus_groups:group",
            "group_id":group.id,
            "base":"plus_lib/listing_frag.html",
            "search_terms":search_terms
            }, context_instance=context)

from apps.plus_lib.utils import hub_name_plural, hub_name
@site_context
def groups(request, site, type='other', template_name='plus_groups/groups.html', current_app='plus_groups'):
    if type == 'hub' :
        head_title = hub_name_plural()
        type_name = hub_name()
        groups = TgGroup.objects.plus_hub_filter(request.user, level='member')
    else:
        head_title = 'Groups'
        type_name = "Group"
        groups = TgGroup.objects.plus_virtual_filter(request.user, level='member')

    return groups_list(request, site, groups, 
                       template_name, head_title, '', type_name=type_name, current_app=current_app)


def groups_list(request, site, groups, template_name, head_title='', head_title_status='', type_name='Group', current_app=None) :

    search_terms = request.GET.get('search', '')
    order = request.GET.get('order')
    if not order:
        order = 'name'
    create = False

    if request.user.is_authenticated() :

        try :
            if current_app == 'plus_groups' :
                site.create_virtual
            else :
                site.create_hub
            create = True
        except Exception, e:
            print "User can't create a group",e
    
    
    context = RequestContext(request, current_app=current_app)

    return render_to_response(template_name, {
            "objects" : groups,
            "order" : order,
            "search_terms":search_terms,
            "search_type":'plus_groups:groups',
            "head_title":head_title,
            "obj_type": type_name,
            "results_label":head_title,
            "create":create,
            'base': "plus_lib/site_listing.html"
            }, context_instance=context)


@login_required
@secure_resource(TgGroup, required_interfaces=['Join','Viewer'])
def join(request, group,  template_name="plus_groups/group.html", current_app='plus_groups', **kwargs):
    group.join(request.user)
    return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id,)))


@login_required
@secure_resource(TgGroup, required_interfaces=['Apply','Viewer'])
def apply(request, group_id, current_app='plus_groups', **kwargs):
    group.apply(request.user)
    return HttpResponseRedirect(reverse(current_app + ':apply_to_group',args=(group.id)))            
    

@login_required
@secure_resource(TgGroup, required_interfaces=['Join','Viewer']) 
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
            group.message_members(request.user, message_header, message_body)
            request.user.message_set.create(message=_("You have successfully messaged everyone in %s"))
            return HttpResponseRedirect(reverse(current_app + ':group',args=(group.id)))
    else :
        form = TgGroupMessageMemberForm()
    return render_to_response(template_name, 
                              {'form' : form,
                               'group': group }, context_instance=RequestContext(request, current_app=current_app))


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
    
    if current_app == 'plus_groups' :
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
    form = AddContentForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data['title']
        type_string = form.cleaned_data['type_string']
        create = getattr(group, "create_" + type_string)
        title = form.cleaned_data['title']
        name = form.cleaned_data['name']

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
            ["CreateResource", _("Resource"), _("Upload a resource")],
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

