from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User

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
    sc = SecurityContext()
    sc.save()
    self.set_security_context(sc)
    return sc

def set_security_context(self, scontext):
    """Set the security context used by this object
    """
    ref = self.get_ref()
    ref.explicit_scontext = scontext
    ref.save()


def get_security_context(self):

    ref = self.get_ref()
    if ref.explicit_scontext:
        return ref.explicit_scontext
    return ref.acquires_from.obj.get_security_context()
    

    
def get_ref(self):
    return self.ref.all()[0]

def acquires_from(self, content_obj):
    ref = self.get_ref()
    ref.acquires_from = content_obj.get_ref()
    ref.save()

from apps.plus_permissions.models import GenericReference, SecurityContext
from django.db.models.signals import post_save

def security_patch(content_type):  
    content_type.add_to_class('ref', generic.GenericRelation(GenericReference))
    content_type.get_ref = get_ref
    content_type.to_security_context = to_security_context
    content_type.set_security_context = set_security_context
    content_type.get_security_context = get_security_context
    content_type.acquires_from = acquires_from
    post_save.connect(create_reference, sender=content_type)

def create_reference(sender, instance=None, **kwargs):
    if instance is None:
        return
    ref = GenericReference(obj=instance)
    ref.save()


