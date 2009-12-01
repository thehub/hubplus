from apps.plus_permissions.exceptions import PlusPermissionsNoAccessException
from apps.plus_permissions.interfaces import secure_wrap
from apps.plus_permissions.default_agents import get_site
from django.http import HttpResponseForbidden
from django.contrib.contenttypes.models import ContentType

import re

def get_resource(cls, resource_id):

    if cls.__name__ == 'User':
        if re.match('[0-9]+',resource_id) :
            resource = cls.objects.get(id=resource_id)
        else :
            resource = cls.objects.get(username=resource_id)
    else:
        try:
            resource=cls.objects.get(pk=resource_id)
        except cls.DoesNotExist:
            resource = None
    return resource

def secure(request, cls, resource_id, required_interfaces=None, with_interfaces=None, all_or_any='ALL'):
    """all_or_any refers to whether the object must have 'ALL' or 'ANY' of the required interfaces
    """
    resource = get_resource(cls, resource_id)
    if not resource:
        return None
    sec_resource = secure_wrap(resource, request.user, interface_names=with_interfaces)
    if required_interfaces:
        check_interfaces(sec_resource, cls, required_interfaces, all_or_any)
    return sec_resource

def check_interfaces(sec_resource, cls, required_interfaces, all_or_any='ALL'):
    count = 0
    for i_name in required_interfaces:
        iface_name = '%s.%s' % (cls.__name__, i_name)
        if iface_name not in sec_resource._interfaces:
            if all_or_any == 'ALL':
                raise PlusPermissionsNoAccessException(cls, sec_resource.id, "You can't call that function")
        else:
            count +=1
            return
    if count <= 1 and all_or_any == 'ANY':
        raise PlusPermissionsNoAccessException(cls, sec_resource.id, "You can't call that function")

def secure_resource(cls=None, with_interfaces=None, required_interfaces=None, obj_schema=None):
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
                data.update(kwargs) # added because we want to keep some params to view eg. class and id in the URL

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
                    required = None
                    with_ifaces = None
                    if isinstance(required_interfaces, dict):
                        required = required_interfaces.get(obj_key, None)
                    if isinstance(with_interfaces, dict):
                        with_ifaces = with_interfaces.get(obj_key, None)
                    sec_resource = secure(request, cls, id, required, with_ifaces)
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
