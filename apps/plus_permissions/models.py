from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from permissionable import *

from apps.hubspace_compatibility.models import TgGroup, Location, Agent
from apps.plus_permissions.interfaces import *


import pickle
import simplejson

import datetime
import ipdb


class SecurityContext :
     """Target is the thing the context is associated with e.g. Group. The thing that we will metaphorically put things "in".
     Context Agent is the 

     """
     target_content_type = models.ForeignKey(ContentType,related_name='blah')
     target_object_id = models.PositiveIntegerField()
     target = generic.GenericForeignKey('target_content_type', 'target_object_id') 
     context_agent_content_type = models.ForeignKey(ContentType,related_name='blah')
     context_agent_object_id = models.PositiveIntegerField()
     context_agent = generic.GenericForeignKey('context_agent_content_type', 'context_angent_object_id')
     # e.g. if permissions are set on a wiki page: context_agent is the group  and the wiki becomes its own context
     #e.g.2 if permission are set on a profile: context_agent is the User and the context is the profile.
     possible_types = []
     slider_agents = []   # order actually matters here
     interfaces  = {}   # {type: [interface_order]}
     contraints = {}    # {type: [contstraints]}  e.g. {wiki:['editor<viewer']}
     defaults  = {}     #{ type: [{interface:default_group},{interface:default_group}}

     def __init__(self, target, json, ):
         """Setup security tags
         """
         self.target = target
         self.json_to_context(json)
         for type
         SecurityTag.create(interface, self).add_agent(new_agent)


     def json_to_context(self, json):
         """Phil, please put json definition of context here. I guess this would be defined in associate with each class that can be a context
         
         How do we represent "dynamic agents"
         Example json : 
         { 'target' : target,
           'possible_types' : ['profile', 'tggroup', 'wikipage', 'etc'] # actually, maybe Django's "model name"  as in the "model" field of the ContentType class
           'slider_agents': [[world_type,world_id],
                             [all_members_type,all_members_is],
                             [$context_agent_type,$context_agent_id], 
                             [ $this_admin_type,$this_admin_id]], 
           'interfaces':{'profile':['Profile.Viewer','Profile.Editor','Profile.PhoneViewer','Profile.EmailViewer', ...],
                         'tggroup':['TgGroup.Viewer','TgGroup.Editor','TgGroup.Join',...],...},
           'constraints':{'profile':[['Profile.Viewer','Profile.Editor'],['Profile.Viewer','Profile.PhoneViewer'],['Profile.Viewer','Profile.EmailViewer'] ...],
                          'defaults':{'profile':['Profile.Viewer':$]}
                          }
         }
                          """
            for agent in slider_agents:
                if agent.startswith('$'):
                    agent = getattr(context, agent[1:])
                else:
                    agent = blah
                    
     def create_security_tag(self, context, interface, agents) :
         # agents here is a list of something like User or TgGroup, NOT an Agent
         tag = SecurityTag(context=context, interface=interface)
         tag.save()
         for agent in agents :
            tag.agents.add(agent.corresponding_agent())
        tag.save()
        return tag
     
     def move_slider(self, new_agent, interface):
         if new_agent in self.slider_agents:
             for agent in slider_agents:
                 if agent not in SecurityTag.objects.filter(interface=interface, context=self).agents:
                     self.add_agent_to_tag()
                 if agent == new_agent:

     def get_slider_level(self, interface):
              
     def add_arbitrary_agent(self, new_agent, interface):
              tag = SecurityTag.objects.filter(interface, self)
              tag.add_agent(new_agent)
              

     def get_tags_on(self, resource) :
         context = resource.get_security_context()
         context_type = ContentType.objects.get_for_model(context)
         return SecurityTag.objects.filter(context_content_type=context_type, context_object_id=context.id)

     def has_permissions(self,resource) :
         return self.get_tags_on(resource).count() > 0
     
     def setup_defaults(self,resource, owner, creator) :
         options = self.make_slider_options(resource,owner,creator)
         self.save_defaults(resource,owner,creator)
         interfaces = self.get_interfaces()
         s = interfaces['Viewer'].make_slider_for(resource,options,owner,0,creator)
         s = interfaces['Editor'].make_slider_for(resource,options,owner,2,creator)
         s = interfaces['Commentor'].make_slider_for(resource,options,owner,1,creator)
        



def make_security_context(obj):
    """Turn an existing object into a security context.
    """
    pass

def set_security_context(obj, security_context=None):
    """Set the security context of an content object.
    """
    if context is None:
        move up the hierarchy until you find one


class SecurityTag(models.Model) :
    interface = models.CharField(max_length=100)
    security_context = models.ForeignKey(SecurityContext)  # revere is securitytag
    agents = models.ManyToManyField(Agent)

    objects = SecurityTagManager()

    def get_context_type(self) :
        return ContentType.objects.get_for_model(self.security_context)

    def __str__(self) :
        return """(%s)Interface: %s, Contexte: %s, Agents: %s""" % (self.id, self.interface,self.context,self.agents)




class PermissionSystem :
    """ This is a high-level interface to the permission system. Can answer questions about permissions without involving 
    the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
    to which anyone is a member)"""

    def __init__(self) :
        self.root_location, created = Location.objects.get_or_create(name='Virtual Hub')
        if created :
            self.root_location.save()

        self.anonyoumous_group = self.get_or_create_group('anonymous', 'World', self.root_location)
        self.all_members_group = self.get_or_create_group('all_members','All Members',self.root_location)
        

    def get_anon_group(self) : 
        """ The anon_group is the root of all groups, representing permissions given even to non members; plus everyone else"""
        return TgGroup.objects.filter(group_name='anonymous')[0]

    def get_security_context(resource):
        

    def has_access(self, agent, resource, interface) :
        """Does the agent have access to this interface in this context
        """
        
        # we're always interested in the security_context of this resource
        context = self.get_security_context(resource)
        context_type = ContentType.objects.get_for_model(context)

        # which agents have access?
        allowed_agents = Agent.objects.filter(securitytag__interface=interface,
                                              securitytag__context_content_type=context_type,
                                              securitytag__context_object_id=context.id)

        allowed_agents = set([a.agent for a in allowed_agents])

        if get_permission_system().get_anon_group() in allowed_agents: 
            # in other words, if this resource is matched with anyone, we don't have to test 
            #that user is in the "anyone" group
            return True

        agents_held = agent.get_enclosure_set()
        if allowed_agents.intersection(agents_held):
            return True

        return False


    def add_permission_manager(self,cls,pm) :
        self.get_interface_factory().add_permission_manager(cls,pm)
        

ps = PermissionSystem()
