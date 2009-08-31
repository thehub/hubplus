

""" This is a high-level interface to the permission system. Can answer questions about permissions without involving 
the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
to which anyone is a member)"""


from apps.plus_permissions.interfaces import secure_wrap, TemplateSecureWrapper

from apps.plus_permissions.models import SecurityTag, SecurityContext, has_access
from apps.hubspace_compatibility.models import Location, TgGroup
from apps.plus_permissions.default_agents import get_anon_user, get_admin_user, get_anonymous_group, get_all_members_group, get_site
from django.http import HttpResponseForbidden

from apps.plus_permissions.exceptions import PlusPermissionsReadOnlyException, PlusPermissionsNoAccessException
from django.contrib.contenttypes.models import ContentType

__all__ = ['secure_wrap', 'TemplateSecureWrapper', 'has_access', 'get_or_create_root_location', 'get_site', 'get_anonymous_group', 'get_all_members_group', 'get_admin_user', 'get_admin_user', 'secure_resource', 'site_context', 'PlusPermissionsNoAccessException', 'PlusPermissionsReadOnlyException']

def get_resource(cls, resource_id):
    if cls.__name__ == 'User':
        resource = cls.objects.get(username=resource_id)
    else:
        resource=cls.objects.get(pk=resource_id)
    return resource

def secure(request, cls, resource_id, required_interfaces=None, with_interfaces=None):
    """
    """
    resource = get_resource(cls, resource_id)
    sec_resource = secure_wrap(resource, request.user, interface_names=with_interfaces)
    if required_interfaces:
        for i_name in required_interfaces:
            iface_name = '%s.%s' % (cls.__name__, i_name)
            if iface_name not in sec_resource._interfaces:
                raise PlusPermissionsNoAccessException(cls, resource_id, "You can't call that function")
    return sec_resource


def secure_resource(cls=None, with_interfaces=None, required_interfaces=None, obj_schema=None) :
    def decorator(f):
        if cls:
            def g(request, resource_id, *args, **kwargs):
                try:
                    sec_resource =  secure(request, cls, resource_id, required_interfaces, with_interfaces)
                except PlusPermissionsNoAccessException:
                    return HttpResponseForbidden(
                        "User %s is not authorized to call %s with interface %s" % (request.user, get_resource(cls, resource_id), required_interfaces[0])
                    )
                return f(request, sec_resource, *args,**kwargs)
            return g
        elif obj_schema:
            def g(request, *args, **kwargs):
                if request.POST:
                    data = request.POST.copy() 
                elif request.GET:
                    data = request.GET.copy()

                    
                for obj_key, obj_types in obj_schema.iteritems():
                    if isinstance(obj_types, list) and len(obj_types) == 1:
                        cls = obj_types[0]
                    elif obj_types == 'any' or isinstance(obj_types, list):
                        classname = data.get(obj_key + '_class', None)
                        if classname:
                            cls = ContentType.objects.get(model=classname.lower()).model_class()
                            if isinstance(obj_types, list):
                                if cls not in obj_types:
                                    raise TypeError(cls.__name__ + " not in " + `list`)
                        else:
                            continue

                    id = data.get(obj_key, None) or data.get(obj_key +'_id', None)
                    sec_resource = secure(request, cls, id)
                    #would be better to introspect the view functions signature here, thus allowing us to use args or kwargs
                    kwargs[obj_key] = sec_resource
                return f(request, *args, **kwargs)
            return g
        else:
            def g(request, *args, **kwargs):
                return f(request, *args, **kwargs)
            return g
    return decorator


def site_context(f) :
    """ wrap this around a view if you want a wrapped site added to the request """
    def g(request, *args, **kwargs):
        user = request.user
        return f(request, get_site(user), *args, **kwargs)

    return g




