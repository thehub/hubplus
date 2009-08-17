
""" This is a high-level interface to the permission system. Can answer questions about permissions without involving 
the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
to which anyone is a member)"""


from apps.plus_permissions.interfaces import secure_wrap, TemplateSecureWrapper

from apps.plus_groups.models import get_or_create_group
from apps.plus_permissions.models import SecurityTag, SecurityContext, has_access
from apps.hubspace_compatibility.models import Location, TgGroup
from apps.plus_permissions.permissionable import get_or_create_root_location

__all__ = ['secure_wrap', 'TemplateSecureWrapper', 'Location', 'TgGroup', 'has_access', 'anonyoumous_group', 'all_members_group', 'get_or_create_root_location']


anonymous_group = TgGroup.objects.get_or_create(group_name='anonymous', display_name='World', place=get_or_create_root_location(), level='public')
all_members_group = TgGroup.objects.get_or_create(group_name='all_members', display_name='All Members', place=get_or_create_root_location(), level='site_member')



def create_security_tag(scontext, interface, agents=[]) :
    # do we need this? 
    if scontext.__class__ != SecurityContext: 
        scontext = scontext.get_ref().explicit_scontext
        print "III", scontext, scontext.__class__
    t = SecurityTag(security_context=scontext, interface=interface)
    t.save()
    for a in agents : 
        t.add_agent(a)
    

def has_interfaces_decorator(interfaces) :
    def decorator(f) :
        def g(request, resource,*args,**kwargs) :
            r2 = secure_wrap(resource,interfaces)
            return f(request, r2,*args,**kwargs)
        return g
    return decorator
            
        

