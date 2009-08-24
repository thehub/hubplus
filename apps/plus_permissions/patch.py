import ipdb
ipdb.set_trace()

from apps.plus_permissions.permissionable import security_patch
from apps.plus_permissions import types
from apps.plus_permissions.types import *
from apps.plus_permissions.models import type_interfaces_map, SliderOptions
from apps.plus_permissions.interfaces import add_creator_interface, add_manage_permissions_interface

from django.db.models.signals import post_save


# Add the create_* interfaces and sliders 
def add_create_interfaces(content_type, child_types):
    for child in child_types:
        key = 'Create%s'%child.__name__
        type_interfaces_map[content_type.__name__][key] = add_creator_interface(child)
        SliderOptions[content_type]['InterfaceOrder'].append(key)



for module in types.__all__:
    print "patching %s"% module
    content_type =  globals()[module].content_type
    child_types  =  globals()[module].child_types
    security_patch(content_type, child_types)
    add_create_interfaces(content_type, child_types)

    type_interfaces_map[content_type.__name__]['ManagePermissions'] = add_manage_permissions_interface()


# The following two patches are being done here, because both 
def site_create_group(self, user, **kwargs):
    from apps.plus_permissions.types.TgGroup import get_or_create
    group, created =  get_or_create(user=user, **kwargs)
    return secure_wrap(group, user)

from apps.plus_permissions.site import Site
Site.create_TgGroup = site_create_group

from apps.profiles.models import Profile, create_profile
post_save.connect(create_profile, sender=User)


from default_agents import CreatorMarker
security_patch(CreatorMarker,[])

from apps.hubspace_compatibility.models import TgGroup
from apps.plus_permissions.types.TgGroup import get_or_create

TgGroup.objects.get_or_create = get_or_create

