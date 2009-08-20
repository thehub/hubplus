
from apps.plus_permissions.permissionable import security_patch
from apps.plus_permissions import types
from apps.plus_permissions.types import *
from apps.plus_permissions.models import type_interfaces_map, SliderOptions
from apps.plus_permissions.interfaces import add_creator_interface, add_manage_permissions_interface

# Add the create_* interfaces and sliders 
def add_create_interfaces(content_type, child_types):
    for child in child_types:
        key = 'Create%s'%child.__class__.__name__
        type_interfaces_map[content_type][key] = add_creator_interface(child)
        SliderOptions[content_type]['InterfaceOrder'].append(key)


for module in types.__all__:
    print "module:" + `module`
    content_type =  globals()[module].content_type
    child_types  =  globals()[module].child_types
    security_patch(content_type, child_types)
    add_create_interfaces(content_type, child_types)
    print "AAA",content_type,content_type.__name__
    type_interfaces_map[content_type.__name__]['ManagePermissions'] = add_manage_permissions_interface()


from django.contrib.auth.models import User
security_patch(User,[])


from default_agents import CreatorMarker
security_patch(CreatorMarker,[])
