from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User
from apps.hubspace_compatibility.models import TgGroup, Location

import datetime

class Interface : pass

class InterfaceFactory :

    def __init__(self) :
        self.all = {}
        self.permission_managers = {}

    def add_type(self,cls) :
        if not self.all.has_key(cls.__name__) :
            self.all[cls.__name__] = {}

    def get_type(self,cls) :
        return self.all[cls.__name__]

    def add_interface(self,cls,name,interfaceClass) :
        self.add_type(cls)
        self.get_type(cls)[name] = interfaceClass


    def get_interface(self,cls,name) :
        return self.get_type(cls)[name]        

    def get_id(self,cls,name) : 
        return '%s.%s' % (cls.__name__,name)

    def add_permission_manager(self,cls,pm) :
        self.permission_managers[cls.__name__] = pm
        pm.register_with_interface_factory(self)

    def get_permission_manager(self,cls) : 
        return self.permission_managers[cls.__name__]


class DefaultAdmin(models.Model) :
    agent_content_type = models.ForeignKey(ContentType,related_name='default_admin_agent')
    agent_object_id = models.PositiveIntegerField()
    agent = generic.GenericForeignKey('agent_content_type', 'agent_object_id')

    resource_content_type = models.ForeignKey(ContentType,related_name='default_admin_resource')
    resource_object_id = models.PositiveIntegerField(null=True)
    resource = generic.GenericForeignKey('resource_content_type', 'resource_object_id')

def default_admin_for(resource) :
    ds = [x for x in DefaultAdmin.objects.all() if x.resource == resource]
    if len(ds) < 1 : 
        return None
    else :
        return ds[0].agent


class AgentNameWrap(object) :
    def __init__(self,inner) :
        self.__dict__['inner'] = inner

    def __getattr__(self, name) :
        if name == 'name' :
            if self.inner.__class__ == User :
                return self.inner.username
            else :
                return self.inner.display_name
        else :
            return getattr(self.inner,name,None)

    def __setattr__(self,name,val) :
        if name != 'name' :
            setattr(self.inner,name,val)
        else :
            if self.inner.__class__ == User :
                self.inner.username = val
            else :
                self.inner.display_name = val
    
 
class SecurityTag(models.Model) :
    name = models.CharField(max_length='50') 
    agent_content_type = models.ForeignKey(ContentType,related_name='security_tag_agent')
    agent_object_id = models.PositiveIntegerField()
    agent = generic.GenericForeignKey('agent_content_type', 'agent_object_id')
 
    interface = models.CharField(max_length='50')

    resource_content_type = models.ForeignKey(ContentType,related_name='security_tag_resource')
    resource_object_id = models.PositiveIntegerField()
    resource = generic.GenericForeignKey('resource_content_type', 'resource_object_id')

    def all_named(self) : 
        return (x for x in SecurityTag.objects.all() if x.name == self.name)

    def has_access(self,agent,resource,interface) :
        for x in (x for x in SecurityTag.objects.all() if x.resource == resource and x.interface == interface) :
            if x.agent == agent : 
                return True
            if agent.is_member_of(x.agent) : 
                return True
        return False

    def __str__(self) :
        return """Agent : %s, Resource : %s, Interface : %s""" % (self.agent,self.resource,self.interface)


_ONLY_INTERFACE_FACTORY = InterfaceFactory()

class PermissionSystem :
    """ This is a high-level interface to the permission system. Can answer questions about permissions without involving 
    the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
    to which anyone is a member)"""

    def get_or_create_group(self,group_name,display_name,place) :
        # note : we can't use get_or_create for TgGroup, because the created date clause won't match on a different day                                     
        # from the day the record was created.                                                                                                              
        xs = TgGroup.objects.filter(group_name=group_name)
        if len(xs) > 0 :
            g = xs[0]
        else :
            g = TgGroup(
                group_name=group_name, display_name=display_name, level='member',
                place=place,created=datetime.date.today()
                )
            g.save()
        return g

    def __init__(self) :
        self.root_location, created = Location.objects.get_or_create(name='root_location')
        if created :
            self.root_location.save()

        self.root_group = self.get_or_create_group('root','root',self.root_location)
        self.all_members_group = self.get_or_create_group('all_members','all members',self.root_location)


    def get_permissions_for(self,resource) :
        return (x for x in SecurityTag.objects.all() if x.resource == resource)

    def has_permissions(self,resource) :
        return len(set(self.get_permissions_for(resource))) > 0 

    def get_anon_group(self) : 
        """ The anon_group is the root of all groups, representing permissions given even to non members; plus everyone else"""
        return TgGroup.objects.filter(group_name='root')[0]

    def get_all_members_group(self) :
        """ The group to which all account-holding "hub-members" belong"""
        return TgGroup.objects.filter(group_name='all_members')[0]

    def has_access(self,agent,resource,interface) :
        t = SecurityTag()
        return t.has_access(agent,resource,interface)

    def delete_access(self,agent,resource,interface) :
        for tag in SecurityTag.objects.filter(interface=interface) :
            if tag.agent == agent and tag.resource==resource : 
                tag.delete()

    def get_interface_factory(self) : 
        return _ONLY_INTERFACE_FACTORY

    def get_permission_manager(self,cls) :
        return self.get_interface_factory().get_permission_manager(cls)

_ONLY_PERMISSION_SYSTEM = PermissionSystem()

def get_permission_system() :
    return _ONLY_PERMISSION_SYSTEM


# Sliders and and permission_managers ____________________________________________________________

class UseSubclassException(Exception) :
    def __init__(self,cls,msg) :
        self.cls = cls
        self.msg = msg

class PermissionManager :
    def get_permission_system(self) :
        return get_permission_system()

    def make_slider(self,**args) :
        raise UseSubclassException(PermissionManager,'Only a subclass of PermissionManager can make sliders')

class NoSliderException(Exception) :
    def __init__(self,cls,name) :
        self.cls = cls
        self.name = name


class Slider :
    """ A Slider is a specialized view of the underlying PermissionSystem.
    As such, it isn't an entity in the database in it's own right, but is used to manipulate 
    the existence or otherwise of particular SecurityTags ...

    A slider is created when a user needs to manipulate the PermissionSystem, and destroyed 
    when no longer relevant.

    The creation or destruction of a slider object represents no change to the permissions.

    When a slider is created, two pieces of fixed information define it : 
      - the resource to which it refers
      - the interface of the resource by which it refers
    These do not change during its life-time.

    The third dimension of the (agent,resource,interface), the agent, is changed by the slider.
    Changing the agent mapped to the resource / interface involves destroying the existing SecurityTag 
    and creating a new one.

    On creation, the slider may infer its status from the database
    
    """

    def __init__(self, tag_name, resource,interface_id,default_agent,options=[]) :
        self.resource = resource
        self.interface_id = interface_id
        self.options = options
        self.tag_name = tag_name

        # start with the default agent
        try :
            self.current_idx = self.options.index(default_agent)
            self.agent = default_agent
        except : 
            self.current_idx = -1
            self.agent = None

        # and over-ride if there's an existing SecurityTag which references one of the agents in our defaults
        for a in (tag.agent for tag in SecurityTag.objects.filter(interface=interface_id) if tag.resource == resource) :
            try : 
                self.current_idx = self.get_options().index(a)
                self.agent = a
                break
            except :
                pass

        if not self.agent is None : # we found a valid default_agent or current value in the database
            self.set_current_option(self.current_idx) # Warning, updates SecurityTag in database

    def get_relevant_tags(self) :
        return (t for t in SecurityTag.objects.filter(interface=self.interface_id) if t.resource == self.resource)

    def print_relevant_tags(self) :
        for t in self.get_relevant_tags():
            print ">> %s, %s, %s, %s" % (AgentNameWrap(t.agent).name, t.interface, t.resource, t.name)

    def get_options(self) :
        return self.options

    def get_current_option(self) :
        return self.options[self.current_idx]

    def set_current_option(self,idx) :
        # set as index of the slider .... is this right? Probably.
        self.current_idx=idx
        _ONLY_PERMISSION_SYSTEM.delete_access(self.agent,self.resource,self.interface_id)
        self.agent = self.options[self.current_idx].agent
        t = SecurityTag(name=self.tag_name,agent=self.agent,resource=self.resource,interface=self.interface_id)
        t.save()


class SliderOption :
    def __init__(self,name,agent) :
        self.name = name
        self.agent = agent

