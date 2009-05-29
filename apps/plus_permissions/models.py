from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic



class Interface :
    def __init__(self,name):
        self.name = name


class OurPost(models.Model) :
    title = models.CharField(max_length='20')

    @classmethod
    def getInterfaces(self) :
        return { 'viewer' : 'viewer', 'editor':'editor', 'commentor':'commentor' }
        return {
        'viewer':Interface('viewer'),
        'editor':Interface('editor'),
        'commentor':Interface('commentor')
        }

    @classmethod
    def getInterface(self,name) :
        return self.getInterfaces()[name]




class SecurityTag(models.Model) :
    name = models.CharField(max_length='20') 

    agent_content_type = models.ForeignKey(ContentType,related_name='security_tag_agent')
    agent_object_id = models.PositiveIntegerField()
    agent = generic.GenericForeignKey('agent_content_type', 'agent_object_id')
 
    interface = models.CharField(max_length='20')
 
    resource_content_type = models.ForeignKey(ContentType,related_name='security_tag_resource')
    resource_object_id = models.PositiveIntegerField()
    resource = generic.GenericForeignKey('resource_content_type', 'resource_object_id')


    def IoN(self,i,res) :
        # if variable i is not an Interface object, we guess it evaluates to 
        # the name of an interface in the dictionary of the resource
        if i.__class__ != Interface : return res.getInterfaces()[i]
        return i

    def filter(self,agent,resource,interface) :
        return (x for x in SecurityTag.objects.all() if (x.agent == agent and x.resource == resource and x.interface == interface) )

    def hasAccess(self,agent,resource,interface) :
        interface = self.IoN(interface,resource)
        for x in self.filter(agent,resource,interface) :
            return True
        return False

    def __str__(self) :
        return """Agent : %s, Resource : %s, Interface : %s""" % (self.agent,self.resource,self.interface)

