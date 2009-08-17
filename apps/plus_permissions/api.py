
""" This is a high-level interface to the permission system. Can answer questions about permissions without involving 
the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
to which anyone is a member)"""

__all__ = ['secure_wrap', 'TemplateSecureWrapper', 'Location', 'TgGroup', 'has_access', 'anonyoumous_group', 'all_members_group', 'get_or_create_root_location']

from apps.plus_permissions.interfaces import secure_wrap, TemplateSecureWrapper
from apps.hubspace_compatibility.models import Location, TgGroup
from apps.plus_permissions.models import has_access
from apps.plus_permissions.permissionable import get_or_create_root_location

from django.contrib.auth.models import User
admin_user = User('admin', 'tom.salfield@the-hub.net', 'blah')
anonyoumous_group = TgGroup.objects.get_or_create(group_name='anonymous', display_name='World', place=get_or_create_root_location(), level='public', user=admin_user)
all_members_group = TgGroup.objects.get_or_create(group_name='all_members', display_name='All Members', place=get_or_create_root_location(), level='site_member', user=admin_user)

