

""" This is a high-level interface to the permission system. Can answer questions about permissions without involving 
the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
to which anyone is a member)"""


from apps.plus_permissions.interfaces import secure_wrap, TemplateSecureWrapper

from apps.plus_permissions.models import SecurityTag, SecurityContext, has_access
from apps.hubspace_compatibility.models import Location, TgGroup
from apps.plus_permissions.default_agents import get_anon_user, get_admin_user, get_anonymous_group, get_all_members_group, get_site
from django.http import HttpResponseForbidden
from apps.plus_permissions.exceptions import PlusPermissionsReadOnlyException, PlusPermissionsNoAccessException


__all__ = ['secure_wrap', 'TemplateSecureWrapper', 'has_access', 'get_or_create_root_location', 'get_site', 'get_anonymous_group', 'get_all_members_group', 'get_admin_user', 'get_admin_user', 'has_interfaces_decorator', 'site_context', 'PlusPermissionsNoAccessException', 'PlusPermissionsReadOnlyException']

def secure(request, cls, resource_id, interface_names, f, *args, **kwargs):
    """
    """
    if cls.__name__ == 'User':
        resource = cls.objects.get(username=resource_id)
    else:
        resource=cls.objects.get(pk=resource_id)
    if interface_names:
        for i_name in interface_names :
            if_name = '%s.%s' % (cls.__name__, i_name)
            if not has_access(request.user, resource, if_name ) :
                return HttpResponseForbidden(
                    "User %s is not authorized to call %s with interface %s" % (request.user, resource, if_name ))

    r2 = secure_wrap(resource, request.user, interface_names=interface_names)
    return f(request, r2, *args,**kwargs)

def has_interfaces_decorator(cls=None, interface_names=None) :
    def decorator(f):
        if cls:
            def g(request, resource_id, *args, **kwargs):
                return secure(request, cls, resource_id, interface_names, f, *args, **kwargs)
            return g
        else:
            def g(request, cls_id, resource_id, *args, **kwargs):
                import ipdb
                ipdb.set_trace()
                #cls
                return secure(request, cls, resource_id, interface_names, f, *args, **kwargs)
            return g            
    return decorator


def site_context(f) :
    """ wrap this around a view if you want a wrapped site added to the request """
    def g(request, *args, **kwargs):
        user = request.user
        return f(request, get_site(user), *args, **kwargs)

    return g




