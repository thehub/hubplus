from django.shortcuts import render_to_response, get_object_or_404

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.db import transaction
from django.utils import simplejson
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from plus_permissions.types.TgGroup import setup_group_security
from apps.plus_permissions.permissionable import create_reference
from apps.plus_permissions.default_agents import get_all_members_group, get_or_create_root_location, get_admin_user, CreatorMarker
from apps.plus_permissions.types.User import setup_user_security
from apps.plus_groups.models import TgGroup
from apps.plus_lib.parse_json import json_view
from django.contrib.auth.models import User
from apps.plus_permissions.api import secure_resource, TemplateSecureWrapper
from apps.plus_permissions.models import GenericReference
from django.template import loader, Context, RequestContext

##############Hubspace Patching######################################
def setup_hubs_security(group, creator):
    """creator will be admin user
    """
    if not creator:
        raise TypeError("We must have a creator to create a group, since otherwise it will be inaccessible")

    create_reference(TgGroup, group)
    if group.level == 'member':
        admin_group = TgGroup.objects.get(place=group.place, level='host')
        setup_hubs_security(admin_group, creator)
        setup_group_security(group, group, admin_group, creator)
    elif group.level == 'host':
        setup_group_security(group, group, group, creator)
    return group

#@login_required
def patch_in_groups(request):
    """Do group security setup for hubspace groups
    XXX patch group names to reflect Location names
    XXX ensure all directors are in the host group
    1. setup a security context for each group passing in context_agent, context_admin and creator
    2. set 'hosts' as a members of the members group, ignore 'directors' groups (they are deprecated - bring on host anarchy!)
    """
    no_security = [group for group in TgGroup.objects.filter(level='member').exclude(place__name='hubplus') if not group.ref.all()]
    admin_user = get_admin_user()
    for group in no_security:
        setup_hubs_security(group, admin_user)
    #this should have setup most of the host groups, but if not
    no_security_host = [group for group in TgGroup.objects.filter(level='host') if not group.ref.all()] #e.g. hubspace superuser and hubspace api
    for group in no_security_host:
        create_reference(TgGroup, group)
        setup_group_security(group, group, group, admin_user)

    return HttpResponse("patched %s hub group's security" % str(len(no_security_host)))

def patch_in_permission_prototype(request):
    for gr in GenericReference.objects.all():
        if not gr.permission_prototype and (isinstance(gr.obj, TgGroup) or isinstance(gr.obj, User)):
            gr.permission_prototype = 'public' 
            gr.save()
    return HttpResponse("patched permission prototype")


#@login_required
def patch_in_profiles(request):
    """create profiles and setup security hubspace users
    """

    site_members_group = get_all_members_group()
    site_members = site_members_group.users.all()

    users = User.objects.all()
    for user in users:
        if user not in site_members:
            site_members_group.users.add(user)

    users = User.objects.filter(profile__isnull=True)
    no_of_users = users.count()

    for user in users:
        create_reference(User, user)
        setup_user_security(user)
        profile = user.create_Profile(user, user=user)
        profile.save()
        print `profile`
    
    return HttpResponse("patched %s users to have profiles" % str(no_of_users))

@secure_resource(obj_schema={'current':'any'})
@json_view
def move_sliders(request, json, current):
    """json is of the form, {interface:[agent_class, agent_id]}
    This should be properly secured by doing everything through permissionable objects on the current resource. i.e. without getting the security context.
    """
    type_name = request.POST['type_name']
    sec_context = current._inner.get_security_context()
    slider_levels = {}
    for interface, agent_tuple in json.iteritems():
        cls = ContentType.objects.get(model=agent_tuple[0].lower()).model_class()
        agent = cls.objects.get(id=agent_tuple[1])
        slider_levels[interface] = agent

    sec_context.move_sliders(slider_levels, type_name, request.user)

    json = {'message':'success'}
    return json


@secure_resource(obj_schema={'current':'any'})
def json_slider_group(request, current):
    """This should be properly secured by doing everything through permissionable objects on the current resource. i.e. without getting the security context.
    """
    sec_context = current._inner.get_security_context()
    custom = False
    if sec_context.get_target() == current._inner:
        custom = True

    slider_sets = sec_context.get_all_sliders(current._inner.__class__, request.user)
    slider_agents = sec_context.get_slider_agents()
    slider_data = []
    for typ, slider_info in slider_sets:
        flags = {}
        slider_agent_rows = []
        for agent_slot, slider_agent in slider_agents:
            interface_status_list = []
            for interface, agent_level in slider_info['interface_levels']:
                #should get the agent more efficiently here, we have it already in reality
                selected = False
                if slider_agent.obj.id == agent_level['id'] and slider_agent.obj.__class__.__name__ == agent_level['classname']:
                    flags[interface] = True
                    selected = True
                css_class = flags.get(interface, False) and 'active' or 'inactive'
                interface_status_list.append((css_class, selected, interface))
            
            slider_agent_rows.append((slider_agent.obj, slider_agent.obj.__class__.__name__, interface_status_list))

        slider_data.append((typ, [header[0] for header in slider_info['interface_levels']],  slider_agent_rows))

    agents = sec_context.get_slider_agents_json()

    t = loader.get_template('plus_permissions/permissions.html')
    c = RequestContext(request, {'current':current, 'current_class':current._inner.__class__.__name__, 'sliders':slider_data, 'custom':custom})
    rendered = t.render(c)
    json = simplejson.dumps({'current_id':current.id,  'sliders':slider_sets, 'agents':agents, 'custom':custom, 'html':rendered})
    
    return HttpResponse(json, mimetype='application/json')

