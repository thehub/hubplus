

""" This is a high-level interface to the permission system. Can answer questions about permissions without involving 
the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
to which anyone is a member)"""


from apps.plus_permissions.interfaces import secure_wrap, TemplateSecureWrapper

from apps.plus_permissions.models import SecurityTag, SecurityContext, has_access
from apps.plus_groups.models import Location, TgGroup
from apps.plus_permissions.default_agents import get_anon_user, get_admin_user, get_anonymous_group, get_all_members_group, get_site
from apps.plus_permissions.decorators import secure, check_interfaces, secure_resource, site_context

from apps.plus_permissions.exceptions import PlusPermissionsReadOnlyException, PlusPermissionsNoAccessException

def has_interface(sec_resource, iface_name):
    if iface_name in sec_resource._interfaces:
        return True
    return False

__all__ = ['secure_wrap', 'TemplateSecureWrapper', 'has_access', 'get_or_create_root_location', 'get_site', 'get_anonymous_group', 'get_all_members_group', 'get_admin_user', 'get_admin_user', 'secure_resource', 'site_context', 'PlusPermissionsNoAccessException', 'PlusPermissionsReadOnlyException', 'secure_resource', 'check_interfaces', 'secure_resource', 'site_context', 'has_interface']





