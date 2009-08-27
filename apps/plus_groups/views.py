from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.db import transaction
from django.utils import simplejson

from apps.hubspace_compatibility.models import TgGroup
from django.core.urlresolvers import reverse


from microblogging.models import Following
from apps.plus_lib.models import DisplayStatus, add_edit_key
from apps.plus_permissions.models import SecurityTag
from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException, SecureWrapper, secure_wrap, TemplateSecureWrapper
from apps.plus_permissions.types.TgGroup import *
from django.contrib.auth.decorators import login_required

from apps.plus_groups.forms import TgGroupForm

from apps.plus_permissions.api import has_interfaces_decorator, site_context
from apps.plus_permissions.default_agents import get_anon_user, get_site

def group(request, group_id, template_name="plus_groups/group.html"):
    group = get_object_or_404(TgGroup, pk=group_id)

    dummy_status = DisplayStatus("Group's Status"," about 3 hours ago")
    
    members = group.get_users()
    print "members :", members

    user = request.user
    if user.is_authenticated():
        if user.is_member_of(group):
            leave = True
        else :
            leave = False
    else:
        leave = False
        
    if not user.is_authenticated():
        user = get_anon_user()
    group = TemplateSecureWrapper(secure_wrap(group, user))

    return render_to_response(template_name, {
            "head_title" : "%s" % group.display_name,
            "head_title_status" : dummy_status,
            "group" : group,
            "extras" : group.groupextras, 
            "leave": leave,
            }, context_instance=RequestContext(request))


def groups(request, template_name='plus_groups/groups.html'):
    
    groups = TgGroup.objects.plus_filter(request.user, level='member' )
    groups = [g for g in groups]
    create = False

    if request.user.is_authenticated():
        print "BBB"
        site = get_site(request.user)
        print "CCC %s" %site.__class__
        try :
            site.create_TgGroup 
            print "DDD"
            create = True
            print "EEE %s"%create
        except Exception, e:
            print "FFF %s", e

            
    print groups
    return render_to_response(template_name, {
            "head_title" : "Groups",
            "head_title_status" : "What a lot of groups",
            "groups" : groups,
            "create" : create,

            }, context_instance=RequestContext(request))


@login_required
@has_interfaces_decorator(TgGroup, ['Join','Viewer'])
def join(request, group,  template_name="plus_groups/group.html"):
    group.join(request.user)
    return HttpResponseRedirect(reverse('group',args=(group.id,)))

    

def apply(request, group_id):
    pass

@login_required
@has_interfaces_decorator(TgGroup, ['Join','Viewer']) 
def leave(request, group, template_name="plus_groups/group.html"):
    group.leave(request.user)
    return HttpResponseRedirect(reverse('group',args=(group.id,)))
    

@login_required
@site_context
def create_group(request, site, template_name="plus_groups/create_group.html"):
    if request.POST :
        form = TgGroupForm(request.user, request.POST)
        print form
    else :
        form = TgGroupForm()
    
    return render_to_response(template_name, {
            "head_title" : "Create New Group",
            "head_title_status" : "",
            "group" : form,

            }, context_instance=RequestContext(request))
