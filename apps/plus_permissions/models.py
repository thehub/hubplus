from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

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
            if agent.isMemberOf(x.agent) : 
                return True
        return False

    def __str__(self) :
        return """Agent : %s, Resource : %s, Interface : %s""" % (self.agent,self.resource,self.interface)

