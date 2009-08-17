from django.db import models
from django.contrib.contenttypes import generic

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


def add_create_method(content_type, content_class, class_name) :
    def f(self,**kwargs) :
        print "Adding class %s" % content_class
        resource = content_class(**kwargs)
        resource.save()
        return resource


    setattr(content_type,'create_%s' % class_name, f)


from apps.plus_permissions.models import GenericReference, SecurityContext
from django.db.models.signals import post_init

def security_patch(content_type, type_list):  
    content_type.add_to_class('ref', generic.GenericRelation(GenericReference))
    content_type.get_ref = get_ref
    content_type.to_security_context = to_security_context
    content_type.set_security_context = set_security_context
    content_type.get_security_context = get_security_context
    content_type.acquires_from = acquires_from

    for typ in type_list :
        add_create_method(content_type, typ, typ.__name__)
        

    post_init.connect(create_reference, sender=content_type)

def create_reference(sender, instance=None, **kwargs):
    if instance is None:
        return
    instance.save()
    ref = GenericReference(obj=instance)
    ref.save()


