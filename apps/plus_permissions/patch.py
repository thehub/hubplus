
from apps.plus_permissions.permissionable import security_patch
from apps.plus_permissions import types
from apps.plus_permissions.types import *

for module in types.__all__:
    content_type =  globals()[module].content_type
    child_types  =  globals()[module].child_types
    security_patch(content_type, child_types)

from django.contrib.auth.models import User
security_patch(User,[])


from default_agents import CreatorMarker
security_patch(CreatorMarker,[])
