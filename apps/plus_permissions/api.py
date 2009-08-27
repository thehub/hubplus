
""" This is a high-level interface to the permission system. Can answer questions about permissions without involving 
the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
to which anyone is a member)"""


from apps.plus_permissions.interfaces import secure_wrap, TemplateSecureWrapper

from apps.plus_permissions.models import SecurityTag, SecurityContext, has_access
from apps.hubspace_compatibility.models import Location, TgGroup
from apps.plus_permissions.default_agents import get_admin_user, get_anonymous_group, get_all_members_group, get_site
from apps.plus_permissions.models import has_access


__all__ = ['secure_wrap', 'TemplateSecureWrapper', 'Location', 'TgGroup', 'has_access', 'anonymous_group', 'all_members_group', 'get_or_create_root_location']

def has_interfaces_decorator(cls, interface_names=None) :
    def decorator(f) :
        def g(request, resource_id, *args, **kwargs) :
            resource=cls.objects.get(id=resource_id)
            r2 = secure_wrap(resource, request.user, interface_names=interface_names)
            return f(request, r2, *args,**kwargs)
        return g
    return decorator


def site_context(f) :
    """ wrap this around a view if you want a wrapped site added to the request """
    def g(request, *args, **kwargs):
        user = request.user
        request['Site'] = get_site(user)
        f(request, *args, **kwargs)

    return g




