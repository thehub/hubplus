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
from apps.plus_permissions.models import SecurityTag
from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException, SecureWrapper, secure_wrap, TemplateSecureWrapper
from apps.plus_permissions.types.TgGroup import *
from django.contrib.auth.decorators import login_required

from apps.plus_groups.forms import TgGroupForm, TgGroupMemberInviteForm, AddContentForm, TgGroupMessageMemberForm

from apps.plus_permissions.api import secure_resource, site_context
from apps.plus_permissions.default_agents import get_anon_user, get_site

from apps.plus_permissions.proxy_hmac import hmac_proxy

from django.contrib.contenttypes.models import ContentType

 
@secure_resource(TgGroup)
def group(request, group, template_name="plus_groups/group.html"):

    user = request.user
    if not user.is_authenticated():
        user = get_anon_user()
        request.user = user 

    
    members = group.get_users()[:10]
    member_count = group.get_no_members()

    hosts = group.get_admin_group().get_users()[:10]
    host_count = group.get_admin_group().get_no_members()

    join = False
    apply = False
    leave = False
    invite = False
    comment = False
    message = False
    add_link = False

    if user.is_authenticated():
        if user.is_direct_member_of(group.get_inner()):
            leave = True
            try :
                group.invite_member
                invite = True
            except Exception, e :# user doesn't have invite permission
                pass

            try :
                group.comment
                comment = True
            except Exception, e: # user doesn't have comment permission
                pass
        else :
            try :
                group.join 
                join = True
            except Exception, e: # user doesn't have join permission
                pass
            try :
                if not join :
                    group.apply
                    apply = True
            except Exception, e : # user doesn't have apply permission
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

    tweets = TweetInstance.objects.tweets_for(group).order_by("-sent") 
    if tweets :
        latest_status = tweets[0]
        dummy_status = DisplayStatus(
            defaultfilters.safe( defaultfilters.urlize(latest_status.html())),
                                 defaultfilters.timesince(latest_status.sent) )
    else :
        dummy_status = DisplayStatus('No status', '')
    
    return render_to_response(template_name, {
            "head_title" : "%s" % group.get_display_name(),
            "head_title_status" : dummy_status,
            "group" : TemplateSecureWrapper(group),
            "target_class" : ContentType.objects.get_for_model(group.get_inner()).id,
            "target_id" : group.get_inner().id,
            "members" : members,
            "member_count" : member_count,
            "leave": leave,
            "join" : join, 
            "apply" : apply, 
            "invite" : invite, 
            "comment" : comment, 
            "message" : message,
            "add_link" : add_link,
            "hosts": hosts,
            "host_count": host_count,
            "tweets" : tweets,
            }, context_instance=RequestContext(request))

from apps.plus_lib.utils import hub_name_plural
@site_context
def groups(request, site, type='other', template_name='plus_groups/groups.html'):
    if type == 'hub' :
        return groups_list(request, site, 
                           TgGroup.objects.plus_hub_filter(request.user, level='member'), 
                           template_name, hub_name_plural(), '')
    else :
        return groups_list(request, site, 
                           TgGroup.objects.plus_virtual_filter(request.user, level='member'),
                           template_name, 'Groups', '')

def groups_list(request, site, groups, template_name, head_title='', head_title_status='') :

    create = False
    if request.user.is_authenticated() :
        try :
            site.create_TgGroup 
            create = True
        except Exception, e:
            print "User can't create a group",e
    

    return render_to_response(template_name, {
            "head_title" : head_title,
            "head_title_status" : head_title_status,
            "groups" : groups,
            "create" : create,

            }, context_instance=RequestContext(request))


@login_required
@secure_resource(TgGroup, required_interfaces=['Join','Viewer'])
def join(request, group,  template_name="plus_groups/group.html"):
    group.join(request.user)
    return HttpResponseRedirect(reverse('group',args=(group.id,)))


@login_required
@secure_resource(TgGroup, required_interfaces=['Apply','Viewer'])
def apply(request, group_id):
    group.apply(request.user)
    return HttpResponseRedirect(reverse('apply_to_group',args=(group.id)))            
    

@login_required
@secure_resource(TgGroup, required_interfaces=['Join','Viewer']) 
def leave(request, group, template_name="plus_groups/group.html"):
    group.leave(request.user)
    return HttpResponseRedirect(reverse('group',args=(group.id,)))

@login_required
@secure_resource(TgGroup, required_interfaces=['Invite', 'Viewer'])
def invite(request, group, template_name='plus_groups/invite.html'):
    if request.POST :
        form = TgGroupMemberInviteForm(request.POST)
        if form.is_valid() :
            invited = form.cleaned_data['user']
            group.invite_member(invited, form.cleaned_data['special_message'], request.user, request.get_host())
            return HttpResponseRedirect(reverse('group',args=(group.id,)))

            
    else :
        form = TgGroupMemberInviteForm()
    return render_to_response(template_name,{
            'form' : form,
            'group' : group,
            },context_instance=RequestContext(request))


@hmac_proxy
@secure_resource(TgGroup,["ManageMembers"])
def add_member(request, group, username, **kwargs) :
    user = get_object_or_404(User, username=username)
    group.add_member(user)
    return HttpResponseRedirect(reverse('group',args=(group.id,)))

@login_required
@secure_resource(TgGroup, required_interfaces=['Message','Viewer'])
def message_members(request, group, **kwargs) :
    template_name = "plus_groups/message_members.html"
    if request.POST :
        form = TgGroupMessageMemberForm(request.POST)
        if form.is_valid() :
            group.message_members(request.user, message_header, message_body)
            request.user.message_set.create(message=_("You have successfully messaged everyone in %s"))
            return HttpResponseRedirect(reverse('group',args=(group.id)))
    else :
        form = TgGroupMessageMemberForm()
    return render_to_response(template_name, 
                              {'form' : form,
                               'group': group }, context_instance=RequestContext(request))


@login_required
@site_context
def create_group(request, site, template_name="plus_groups/create_group.html"):
    if request.POST :
        form = TgGroupForm(request.POST)
        
        if not form.is_valid() :
            print form.errors
        else :
            group = form.save(request.user, site)
            return HttpResponseRedirect(reverse('group', args=(group.id,)))
    else :
        form = TgGroupForm()
    
    return render_to_response(template_name, {
            "head_title" : "Create New Group",
            "head_title_status" : "",
            "group" : form,
            "form" : form,
            }, context_instance=RequestContext(request))




@login_required
@secure_resource(TgGroup)
def group_field(request, group, classname, fieldname, *args, **kwargs) :
    """ Get the value of one field from the group, so we can write an ajaxy editor """
    return one_model_field(request, p, fieldname, kwargs.get('default', ''), TgGroupForm)


@login_required
@secure_resource(obj_schema={'group':[TgGroup]})
def add_content_object(request, group):
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
        return HttpResponse('redirect:' + reverse('edit_' + type_string, args=[group.id, obj.name]))
        
        #redirect to the edit page
        #return HttpResponseRedirect(reverse('edit_' + type_string, args=[group.id, obj.name]))
    
    return add_content_form(request, group.id, form)

 
def possible_create_interfaces():
    """return tuples of form, interface string, label, subtext
    """
    return [["CreateWikiPage", _("Page"), _("Create new wiki page")], 
            ["CreateUpload", _("File"), _("Upload a file")],
            ["CreateNews", _("News"), _("Create a new posting")],
            ["CreateEvent", _("Events"), _("Create a new event")]]


@login_required
@secure_resource(TgGroup)
def add_content_form(request, group, form=None):
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
    return render_to_response("plus_groups/add_content.html", {'group':group, 'possible_interfaces': possible_interfaces, 'can_add':can_add, 'form':form})



@json_view
def autocomplete(request, j=None):
    """filter groups to see which ones this user can add content too. Check that the user can create at least something on the groups that we autocomplete for them
    """
    user = request.user
    q = request.GET['q']
    limit = request.GET['limit']  
    groups = TgGroup.objects.plus_filter(user, interface_names=['Viewer', 'CreateWikiPage'], required_interfaces=['CreateWikiPage'], all_or_any='ANY', display_name__istartswith=q, level__in=['host', 'member'], limit=6)

    options = [{'display_name':group.display_name, 'id':str(group.id), 'interfaces':[iface.split('.')[1] for iface in group._interfaces]} for group in groups]
    return options

