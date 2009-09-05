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
from apps.plus_permissions.models import SecurityTag
from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException, SecureWrapper, secure_wrap, TemplateSecureWrapper
from apps.plus_permissions.types.TgGroup import *
from django.contrib.auth.decorators import login_required

from apps.plus_groups.forms import TgGroupForm

from apps.plus_permissions.api import secure_resource, site_context
from apps.plus_permissions.default_agents import get_anon_user, get_site



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
            "head_title" : "%s" % group.display_name,
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
    groups = [g for g in groups]

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

    
def apply(request, group_id):
    pass
    

@login_required
@secure_resource(TgGroup, required_interfaces=['Join','Viewer']) 
def leave(request, group, template_name="plus_groups/group.html"):
    group.leave(request.user)
    return HttpResponseRedirect(reverse('group',args=(group.id,)))




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
