from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import UserManager, User

from apps.plus_lib.models import extract
from apps.plus_permissions.interfaces import secure_wrap
from apps.plus_permissions.decorators import check_interfaces
from apps.plus_permissions.exceptions import PlusPermissionsNoAccessException

from django.conf import settings

class MissingSecurityContextException(Exception): 
    def __init__(self, cls, security_context) :
        self.cls = cls
        self.security_context = security_context
        self.msg = 'Missing %s when creating a %s' % (context,cls)


class PermissionableManager(models.Manager):
    # if a permission_agent is passed, only get or filter items which 
    # pass a security check
    def plus_filter(self, p_user, interface_names=None, required_interfaces=None, all_or_any='ALL', limit=None, distinct=None, **kwargs):
        """XXX this should itself be evalutated "lazily" e.g. when indexed in the same way as the filter statement which it uses.
        """            
        if not interface_names:
            interface_names = ['Viewer']
        resources = super(self.__class__, self).filter(**kwargs)
        if distinct:
            resources = resources.distinct()

        if limit:
            high_index = min(limit*2, resources.count())
            secured = self.secure_results_set(resources[0:high_index], p_user, interface_names=interface_names, required_interfaces=required_interfaces, all_or_any=all_or_any)
            while len(secured) < limit and high_index < resources.count():
                offset = high_index
                high_index = high_index * float(limit) / len(secured)
                high_index = min(high_index, resources.count())
                secured += self.secure_results_set(resources[offset:high_index]) 
            return secured
        else: 
            return self.secure_results_set(resources, p_user, interface_names=interface_names, required_interfaces=required_interfaces, all_or_any=all_or_any)

    def secure_results_set(self, resources, p_user, interface_names=None, required_interfaces=None, all_or_any='ALL'):
        wrapped_resources = []
        for resource in resources:
            wrapped = secure_wrap(resource, p_user, interface_names=interface_names)
            if required_interfaces:
                try:
                    check_interfaces(wrapped, resource.__class__, required_interfaces=required_interfaces, all_or_any=all_or_any)
                    wrapped_resources.append(wrapped)
                except PlusPermissionsNoAccessException:
                    pass
            else:
                wrapped_resources.append(wrapped)
        return wrapped_resources


    def plus_get(self, p_user, interface_names=None, **kwargs) :
        a = super(self.__class__, self).get(**kwargs)
        return secure_wrap(a, p_user, interface_names=interface_names)
 
    def plus_count(self, p_user, **kwargs) :
        count = 0
        for res in self.plus_filter(p_user, **kwargs) :
            count = count + 1
        return count

    def is_custom(self) : 
        return True

class UserPermissionableManager(UserManager, PermissionableManager) :
    pass

class TgGroupPermissionableManager(PermissionableManager) :
    """ NB: that this class allows us to search for "virtual" groups (ie. online groups) or 
        real "hubs". The name of the virtual group is now controlled by the setting "VIRTUAL_HUB_NAME".
        Database will have to be recreated or patched with this name"""

    def virtual(self):
        query = self.filter(level='member').exclude(group_type=settings.GROUP_HUB_TYPE)

        for id in settings.HIDDEN_GROUPS :
            query = query.exclude(id=id)
        return query

    def hubs(self) :
        return self.filter(level='member',group_type=settings.GROUP_HUB_TYPE)


#    def plus_hub_filter(self, p_user, **kwargs) :
        # bloody django templating language ... why does it work with comprehensions but not generator expressions?
        # XXX needs to be fixed when we work out our lazy filter
#        return [group for group in self.plus_filter(p_user, **kwargs) if group.get_inner().place.name != settings.VIRTUAL_HUB_NAME]

#    def plus_virtual_filter(self, p_user, **kwargs) :
#        kwargs['place__name']=settings.VIRTUAL_HUB_NAME # adding another criteria to query
#        return self.plus_filter(p_user, **kwargs)



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
    # copy the tags and therefore the permissions to the new sec context
    new_sc = self.to_security_context()
    new_sc.context_agent = original_sc.context_agent
    new_sc.context_admin = original_sc.context_admin
    new_sc.save()

    types = [self.__class__] + PossibleTypes[self.__class__]
    applicable_interfaces = []
    for typ in types:
        interfaces = [typ.__name__ + '.' + iface for iface in get_interface_map(typ.__name__)]
        applicable_interfaces.extend(interfaces)
    for tag in original_sc.get_tags():
        if tag.interface in applicable_interfaces:
            tag.clone_for_context(new_sc)

    return new_sc

def use_acquired_security_context(self):
    sc = self.get_security_context()
    sc.target.clear()
    sc.delete()
    # check that related security tags are deleted here
    sc = self.get_security_context()
    return sc

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
        try:
            ref.acquired_scontext = ref.acquires_from.obj.get_security_context()
            ref.save()
        except Exception, e:
            print e
            raise e
    return ref.acquired_scontext
    
def get_ref(self):
    return self.ref.all()[0]

def acquires_from(self, content_obj):
    ref = self.get_ref()
    assert(content_obj.get_ref())
    ref.acquires_from = content_obj.get_ref()
    ref.save()
    return ref

def get_creator(self):
    return self.get_ref().creator


def add_create_method(content_type, child_type) :

    def f(self, creator, **kwargs) :
        # check for validity of the entered name
        if hasattr(child_type, 'check_name') and 'name' in kwargs and 'in_agent' in kwargs:
            child_type.check_name(kwargs['name'], kwargs['in_agent'])
        resource = child_type(**kwargs)
        resource.save()
        # now create its security_context etc.
        resource.acquires_from(self)
        ref = resource.get_ref()
        ref.creator = creator
        ref.save()
        assert(resource.get_creator()==creator)
        return secure_wrap(resource, creator)

    
    setattr(content_type,'create_%s' % child_type.__name__, f)



from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException

def move_sliders(self, interface_level_map, type_name, user):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.move_sliders(interface_level_map, type_name, user)

def add_arbitrary_agent(self, new_agent, interface, p_user):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.add_arbitrary_agent(new_agent, interface, p_user)
    else :
        raise Exception("Shouldn't try to assign arbitrary agent to content_type %s which doesn't have over-ridden security_context" % self)

def remove_arbitrary_agent(self, old_agent, interface, p_user):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.remove_arbitrary_agent(old_agent, interface, p_user)
    else :
        raise Exception("Shouldn't try to remove arbitrary agent to content_type %s which doesn't have over-ridden security_context" %self)


def get_all_sliders(self, type, user):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.get_all_sliders(type, user)

def get_type_slider(self, type_name, user):
    scontext = self.get_ref().explicit_scontext
    if scontext:
        return scontext.get_type_slider(type_name, user)

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
    

def s_eq(self, other):
    """Secure Equality : compares self and other directly and the _inner of each with each."""
    if self == other : return True
    try :
        if self == other.get_inner() : return True
    except :
        return False
    return False


def get_class(self):
    return self.__class__.__name__

from apps.plus_permissions.models import GenericReference, SecurityContext
from django.db.models.signals import post_save

def security_patch(content_type, type_list):
    print "patching %s" %content_type
    content_type.add_to_class('ref', generic.GenericRelation(GenericReference))
    content_type.get_ref = get_ref
    content_type.to_security_context = to_security_context
    content_type.set_security_context = set_security_context
    content_type.get_security_context = get_security_context
    content_type.acquires_from = acquires_from
    content_type.get_tag_for_interface = get_tag_for_interface
    content_type.create_custom_security_context = create_custom_security_context
    content_type.use_acquired_security_context = use_acquired_security_context
    content_type.move_sliders = move_sliders
    content_type.add_arbitrary_agent = add_arbitrary_agent
    content_type.remove_arbitrary_agent = remove_arbitrary_agent
    content_type.get_all_sliders = get_all_sliders
    content_type.get_slider_level = get_slider_level
    content_type.get_creator = get_creator
    content_type.get_class = get_class
    content_type.s_eq = s_eq

    for typ in type_list:
        add_create_method(content_type, typ)
        
    
    if content_type == User:
        content_type.add_to_class('objects', UserPermissionableManager())
    elif content_type.__name__ == 'TgGroup':
        content_type.add_to_class('objects', TgGroupPermissionableManager())
    else :
         content_type.add_to_class('objects', PermissionableManager())

    post_save.connect(create_reference, sender=content_type)


def create_reference(sender, instance=None, **kwargs):
    if instance is None:
        return
    content_type = ContentType.objects.get_for_model(instance)
    if GenericReference.objects.filter(content_type=content_type,
                                       object_id=instance.id).count() < 1:
        ref = GenericReference(obj=instance)
        ref.save()

