from django.db import models


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

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


class SecurityTag(models.Model) :
    name = models.CharField(max_length='20') 

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

    def __init__(self) :

        self.root_location, created = Location.objects.get_or_create(name='root_location')
        if created :
            self.root_location.save()

        # note : we can't use get_or_create for TgGroup, because the created date clause won't match on a different day 
        # from the day the record was created.
        xs = TgGroup.objects.filter(group_name='root')
        if len(xs) > 0 : 
            self.root_group = xs[0]
        else :
            self.root_group = TgGroup(
                group_name='root',display_name='root',level='member',
                place=self.root_location, created=datetime.date.today()
                )
            self.root_group.save()


    def get_permissions_for(self,resource) :
        return (x for x in SecurityTag.objects.all() if x.resource == resource)

    def get_anon_group(self) : 
        """ The anon_group is the root of all groups, representing permissions given even to non members; plus everyone else"""
        return TgGroup.objects.filter(group_name='root')[0]

    def has_access(self,agent,resource,interface) :
        t = SecurityTag()
        return t.has_access(agent,resource,interface)

    def get_interface_factory(self) : 
        return _ONLY_INTERFACE_FACTORY

_ONLY_PERMISSION_SYSTEM = PermissionSystem()

def get_permission_system() :
    return _ONLY_PERMISSION_SYSTEM

class PermissionManager :
    def get_permission_system(self) :
        return get_permission_system()

class Slider :
    def get_options(self) :
        return self.options

    def get_current_option(self) :
        return self.options[self.idx_current]

    def set_current_option(self,idx) :
        self.idx_current = idx

class SliderOption :
    def __init__(self,name) :
        self.name = name
