from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import UserManager, User

from apps.plus_lib.models import extract

class MissingSecurityContextException(Exception): 
    def __init__(self, cls, security_context) :
        self.cls = cls
        self.security_context = security_context
        self.msg = 'Missing %s when creating a %s' % (context,cls)


class MissingSecurityContextException(Exception): 
    def __init__(self, cls, security_context) :
        self.cls = cls
        self.security_context = security_context
        self.msg = 'Missing %s when creating a %s' % (context,cls)



class PermissionableManager(models.Manager) :
    # if a permission_agent is passed, only get or filter items which 
    # pass a security check
    def plus_filter(self,**kwargs) : 
        from apps.plus_permissions.models import has_access
        if not kwargs.has_key('permission_agent') :
            return super(self.__class__,self).filter(**kwargs)
        else :
            from apps.plus_permissions.interfaces import SecureWrapper, secure_wrap
            agent = kwargs['permission_agent']
            del kwargs['permission_agent']

            return (secure_wrap(a, agent)  
                    for a in super(self.__class__,self).filter(**kwargs) 
                    if has_access(agent,a,'%s.%s'%(self.__class__,'Viewer')))
        
    def plus_get(self,**kwargs) :

        if not kwargs.has_key('permission_agent') :
            return super(self.__class__,self).get(**kwargs)
        else :
            from apps.plus_permissions.interfaces import SecureWrapper, secure_wrap
            agent = kwargs['permission_agent']
            del kwargs['permission_agent']
            a = super(self.__class__,self).get(**kwargs)
            return secure_wrap(a, agent)
 
    def plus_count(self, **kwargs) :
        count = 0
        for res in self.plus_filter(**kwargs) :
            count = count+1
        return count

    def is_custom(self) : 
        return True

class UserPermissionableManager(UserManager) :
    # if a permission_agent is passed, only get or filter items which 
    # pass a security check
    # NOTE : this is a special version of PermissionableManager above, which inherits from UserManager
    # I've copied and pasted because I'm not sure if the inheritance diamond works 
    # if we mixin the ordinary PermissionableManager with UserManager and don't have time to investigate
    def plus_filter(self,**kwargs) : 
        from apps.plus_permissions.models import has_access
        if not kwargs.has_key('permission_agent') :
            return super(self.__class__,self).filter(**kwargs)
        else :
            from apps.plus_permissions.interfaces import SecureWrapper, secure_wrap
            agent = kwargs['permission_agent']
            del kwargs['permission_agent']

            return (secure_wrap(a, agent)  
                    for a in super(self.__class__,self).filter(**kwargs) 
                    if has_access(agent,a,'%s.%s'%(self.__class__,'Viewer')))
        
    def plus_get(self,**kwargs) :

        if not kwargs.has_key('permission_agent') :
            return super(self.__class__,self).get(**kwargs)
        else :
            from apps.plus_permissions.interfaces import SecureWrapper, secure_wrap
            agent = kwargs['permission_agent']
            del kwargs['permission_agent']
            a = super(self.__class__,self).get(**kwargs)
            return secure_wrap(a, agent)
 
    def plus_count(self, **kwargs) :
        count = 0
        for res in self.plus_filter(**kwargs) :
            count = count+1
        return count

    def is_custom(self) : 
        return True


def to_security_context(self):
    """Turn an existing object into a security context.
    """    
    if self.get_ref().explicit_scontext :
        # if one already exists, return it (PJ)
        return self.get_ref().explicit_scontext
    sc = SecurityContext()
    sc.save()
    self.set_security_context(sc)
    return sc

from apps.plus_permissions.models import get_interface_map, PossibleTypes

def create_custom_security_context(self) :
    original_sc = self.get_security_context()
    # create a new sc
    # set it's agent and admin
    # copy the tags
    # copy the permissions

    new_sc = self.to_security_context()
    new_sc.get_context_agent()  #the first this is called it will set the context agent
    new_sc.get_context_admin()
    new_sc.save()

    types = [self.__class__] + PossibleTypes[self.__class__]
    applicable_interfaces = []
    for typ in types:
        interfaces = get_interface_map(typ.__name__)
        applicable_interfaces.extend(interfaces)
    for tag in original_sc.get_tags():
        if tag.interface in applicable_interfaces:
            tag.clone_for_context(new_sc)

    return new_sc

def set_security_context(self, scontext):
    """Set the security context used by this object
    """
    ref = self.get_ref()
    #if we are passing in a target, the get its security context 
    ref.explicit_scontext = scontext
    ref.save()


def get_security_context(self):
    """Get the security context for this object """
    ref = self.get_ref()
    if ref.explicit_scontext:
        return ref.explicit_scontext
    elif ref.acquired_scontext:
        return ref.acquired_scontext
    else:
        self.acquired_scontext = ref.acquires_from.obj.get_security_context()
    return self.acquired_scontext
    
def get_ref(self):
    return self.ref.all()[0]

def acquires_from(self, content_obj):
    ref = self.get_ref()
    ref.acquires_from = content_obj.get_ref()
    ref.save()



def add_create_method(content_type, child_type) :

    def f(self,**kwargs) :
        permission_agent = extract(kwargs, 'permission_agent')

        resource = child_type(**kwargs)
        resource.save()

        # now create its security_context etc.        
        resource.acquires_from(self)
        if permission_agent :
            resource = secure_wrap(resource, permission_agent)
        return resource


    setattr(content_type,'create_%s' % child_type.__name__, f)

from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException

def move_sliders(self, interface_level_map, type_name, user):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.move_sliders(interface_level_map, type_name, user)

def add_arbitrary_agent(self, interface, user):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.add_arbitrary_agent(old_agent, interface, user)

def remove_arbitrary_agent(self, old_agent, interface, user):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.remove_arbitrary_agent(old_agent, interface, user)


def get_all_sliders(self, type):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.get_all_sliders(type)

def get_type_slider(self, type_name):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.get_type_slider(type_name)

def get_slider_level(self, interface):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.get_slider_level(interface)


def get_tag_for_interface(self, interface) :
    """ Get the tag which links a resource and interface
    """
    from models import SecurityTag
    if not SecurityTag.objects.filter(security_context=self.get_security_context(),
                                   interface=interface).count() > 0 : 
        return None
    return SecurityTag.objects.get(security_context=self.get_security_context(),
                                   interface=interface)
    


from apps.plus_permissions.models import GenericReference, SecurityContext
from django.db.models.signals import post_init

def security_patch(content_type, type_list):  
    content_type.add_to_class('ref', generic.GenericRelation(GenericReference))
    content_type.get_ref = get_ref
    content_type.to_security_context = to_security_context
    content_type.set_security_context = set_security_context
    content_type.get_security_context = get_security_context
    content_type.acquires_from = acquires_from
    content_type.get_tag_for_interface = get_tag_for_interface
    content_type.create_custom_security_context = create_custom_security_context
    content_type.move_sliders = move_sliders

    for typ in type_list :
        add_create_method(content_type, typ)
        

    if content_type == User:
         content_type.add_to_class('objects',UserPermissionableManager())
    else :
         content_type.add_to_class('objects',PermissionableManager())

    post_init.connect(create_reference, sender=content_type)

def create_reference(sender, instance=None, **kwargs):
    if instance is None:
        return
    instance.save()
    ref = GenericReference(obj=instance)
    ref.save()


