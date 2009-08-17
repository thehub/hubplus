
from apps.plus_permissions.permissionable import security_patch
from apps.plus_permissions import types
from apps.plus_permissions.types import *
for module in types.__all__:
    content_type =  globals()[module].content_type
    security_patch(content_type)
