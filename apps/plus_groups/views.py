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

from microblogging.models import Following
from apps.plus_lib.models import DisplayStatus, add_edit_key
from apps.plus_permissions.models import SecurityTag
from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException, SecureWrapper, secure_wrap, TemplateSecureWrapper
from apps.plus_permissions.types.TgGroup import *
from django.contrib.auth.decorators import login_required


from apps.plus_permissions.api import has_interfaces_decorator

def group(request, group_id, template_name="plus_groups/group.html"):
    group = get_object_or_404(TgGroup, pk=group_id)
    group = TemplateSecureWrapper(secure_wrap(group, request.user))

    dummy_status = DisplayStatus("Group's Status"," about 3 hours ago")
    
    members = group.users
    return render_to_response(template_name, {
            "head_title" : "%s" % group.display_name,
            "head_title_status" : dummy_status,
            "group" : group,
            "extras" : group.groupextras, 
            }, context_instance=RequestContext(request))


def groups(request, template_name='plus_groups/groups.html'):
    groups = TgGroup.objects.filter(level='member')
    groups = [g for g in groups]
    print groups
    return render_to_response(template_name, {
            "head_title" : "Groups",
            "head_title_status" : "What a lot of groups",
            "groups" : groups,

            }, context_instance=RequestContext(request))


@has_interfaces_decorator(TgGroup, [TgGroupJoin])
def join(request, group):
    group.join(request.user)
    return render_to_response(template_name, {
            "head_title" : "%s" % group.display_name,
            "head_title_status" : dummy_status,
            "group" : group,
            "extras" : group.groupextras, 
            }, context_instance=RequestContext(request))
    

def apply(request, group_id):
    pass
