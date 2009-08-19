from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

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
    # XXX ... add the actual wrapper to the output of these functions

    def filter(self,**kwargs) : 
        if not kwargs.has_key('permission_agent') :
            return super(self.__class__,self).filter(**kwargs)
        else :
            from apps.plus_permissions.interfaces import SecureWrapper, secure_wrap
            agent = kwargs['permission_agent']
            del kwargs['permission_agent']

            return (a  
                    for a in super(self.__class__,self).filter(**kwargs) 
                    if has_access(agent,a,get_interface_map(self.__class__,'Viewer')))
        


    def get(self,**kwargs) :
        if not kwargs.has_key('permission_agent') :
            return super(self.__class__,self).get(**kwargs)
        else :
            from apps.plus_permissions.interfaces import SecureWrapper, secure_wrap
            agent = kwargs['permission_agent']
            del kwargs['permission_agent']
            a = super(self.__class__,self).get(**kwargs)
            #return secure_wrap(a,...)
            return a
 

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

def make_custom_security_context(self) :
    original_sc = self.get_security_context()
    new_sc = self.to_security_context()
    # now we need to call set_up for the new_sc, but we
    # need it to know the type of the previous security context
    # eg. if this is an OurPost, it we still need to know we're in a TgGroup
    new_sc.set_up(root_type=original_sc.__class__)
    return new_sc

def set_security_context(self, scontext):
    """Set the security context used by this object
    """
    ref = self.get_ref()
    if scontext.__class__ != SecurityContext: 
        scontext = scontext.get_ref().explicit_scontext
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
        resource = child_type(**kwargs)
        resource.save()

        # now create its security_context etc.        
        resource.acquires_from(self)
        return resource


    setattr(content_type,'create_%s' % child_type.__name__, f)


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
    content_type.make_custom_security_context = make_custom_security_context
          

    for typ in type_list :
        add_create_method(content_type, typ)
        

    post_init.connect(create_reference, sender=content_type)

def create_reference(sender, instance=None, **kwargs):
    if instance is None:
        return
    instance.save()
    ref = GenericReference(obj=instance)
    ref.save()


