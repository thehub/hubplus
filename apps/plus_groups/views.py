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


from microblogging.models import Following
from apps.plus_lib.models import DisplayStatus, add_edit_key
from apps.plus_lib.parse_json import json_view
from apps.plus_permissions.models import SecurityTag
from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException, SecureWrapper, secure_wrap, TemplateSecureWrapper
from apps.plus_permissions.types.TgGroup import *
from django.contrib.auth.decorators import login_required

from apps.plus_groups.forms import TgGroupForm, TgGroupMemberInviteForm

from apps.plus_permissions.api import secure_resource, site_context
from apps.plus_permissions.default_agents import get_anon_user, get_site


from messages.models import Message
def message_user(sender, recipient, subject, body) :
    m = Message(subject=subject, body=body, sender = sender, recipient=recipient)
    m.save()


    #parent_msg = models.ForeignKey('self', related_name='next_messages', null=True, blank=True, verbose_name=_("Parent message"))
    #sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
    #read_at = models.DateTimeField(_("read at"), null=True, blank=True)
    #replied_at = models.DateTimeField(_("replied at"), null=True, blank=True)
    #sender_deleted_at = models.DateTimeField(_("Sender deleted at"), null=True, blank=True)
    #recipient_deleted_at = models.DateTimeField(_("Recipient deleted at"), null=True, blank=True)



@secure_resource(TgGroup)
def group(request, group, template_name="plus_groups/group.html"):

    user = request.user
    if not user.is_authenticated():
        user = get_anon_user()
        request.user = user 

    dummy_status = DisplayStatus("Group's Status"," about 3 hours ago")
    
    members = group.get_users()[:10]
    member_count = group.get_no_members()

    hosts = group.get_admin_group().get_users()[:10]
    host_count = group.get_admin_group().get_no_members()

    join = False
    apply = False
    leave = False
    if user.is_authenticated():
        if user.is_direct_member_of(group.get_inner()):
            leave = True
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
        
    

    return render_to_response(template_name, {
            "head_title" : "%s" % group.get_display_name(),
            "head_title_status" : dummy_status,
            "group" : TemplateSecureWrapper(group),
            "members" : members,
            "member_count" : member_count,
            "leave": leave,
            "join" : join, 
            "apply" : apply, 
            "hosts": hosts,
            "host_count": host_count,
            }, context_instance=RequestContext(request))


def groups(request, template_name='plus_groups/groups.html'):
    
    groups = TgGroup.objects.plus_filter(request.user, level='member')
    #groups = [g for g in groups]

    create = False

    if request.user.is_authenticated():
        site = get_site(request.user)
        try :
            site.create_TgGroup 
            create = True
        except Exception, e:
            print "AAA",e

    print groups
    return render_to_response(template_name, {
            "head_title" : "Groups",
            "head_title_status" : "What a lot of groups",
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
            invitee = form.cleaned_data['user']
            message_user(request.user, invitee, 'Invitation to join %s' % group.get_display_name(), """You have been invited to join %s. <a href="">Click here to a
ccept</a>""" % group.get_display_name())
            message_user(request.user, request.user, "Invitation sent", """You have invited %s to join %s""" % (invitee.get_display_name(), group.get_display_name()))
            invitee.message_set.create(message="""You have been invited to join %s. <a href="">Click here to accept</a>""")

            return HttpResponseRedirect(reverse('group',args=(group.id,)))

            
    else :
        form = TgGroupMemberInviteForm()
    return render_to_response(template_name,{
            'form' : form,
            'group' : group,
            },context_instance=RequestContext(request))


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

            }, context_instance=RequestContext(request))




@login_required
@secure_resource(TgGroup)
def group_field(request, group, classname, fieldname, *args, **kwargs) :
    """ Get the value of one field from the group, so we can write an ajaxy editor """
    return one_model_field(request, p, fieldname, kwargs.get('default', ''), TgGroupForm)


@login_required
@secure_resource(obj_schema={'group':[TgGroup]})
def add_content_object(request, group):
    type_string = request.POST['create_iface'].split('Create')[1]
    create = getattr(group, "create_" + type_string)
    title = request.POST['title']
    name = title.replace(' ', '_')

    #ensure name is unique for group
    #if it is not -- what? a) raise error to user
    obj = create(request.user, title=title, name=name)
    
    return HttpResponseRedirect(reverse('edit_' + type_string, args=(group.id)))
   
 
def possible_create_interfaces():
    """return tuples of form, interface string, label, subtext
    """
    return [["CreateWikiPage", _("Page"), _("Create new wiki page")], 
            ["CreateUpload", _("File"), _("Upload a file")],
            ["CreateNews", _("News"), _("Create a new posting")],
            ["CreateEvent", _("Events"), _("Create a new event")]]


@login_required
@secure_resource(TgGroup)
def add_content_form(request, group):
    possible_interfaces = possible_create_interfaces()
    _interfaces = [g.split('.')[1] for g in group._interfaces]
    for iface in possible_interfaces:
        if iface[0] in _interfaces:
            iface.append(True)
        else:
            iface.append(False)

    return render_to_response("plus_groups/add_content.html", {'group':group, 'possible_interfaces': possible_interfaces})



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

