
""" This is a high-level interface to the permission system. Can answer questions about permissions without involving 
the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
to which anyone is a member)"""

__all__ = ['secure_wrap', 'TemplateSecureWrapper', 'Location', 'TgGroup', 'has_access', 'anonyoumous_group', 'all_members_group', 'get_or_create_root_location']

from apps.plus_permissions.interfaces import secure_wrap, TemplateSecureWrapper
from apps.hubspace_compatibility.models import Location, TgGroup
from apps.plus_permissions.default_agents import get_admin_user, get_anonymous_group, get_all_members_group
from apps.plus_permissions.models import has_access
