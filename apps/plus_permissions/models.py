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


class SecurityContext(models.Model):
     """Target is the thing the context is associated with e.g. Group. The thing that we will metaphorically put things "in".
     Context Agent is the 

     """
     def set_up(self):
         self.json_to_context(json)
         for type in json_to_context:
              for interface in type:
                   tag = SecurityTag.get_or_create(interface, self)
                   self.add_default_agents(tag)
         self.set_context_agent()

     def add_default_agents(self, tag):
          pass

     context_agent = models.ForeignKey('Agent', null=True) #The agent which this security context is associated with
     def set_context_agent(self, agent):
          if self.context_agent:
               return context_agent
          self.context_agent = agent

     possible_types = models.TextField()
     slider_agents = models.TextField()  # order actually matters here
     interfaces  = models.TextField()    # {type: [interface_order]}
     contraints = models.TextField()     # {type: [contstraints]}  e.g. {wiki:['editor<viewer']}
     defaults  = models.TextField()      #{ type: [{interface:default_group},{interface:default_group}}



     def json_to_context(self, json):
         """
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
                         pass

     def get_slider_level(self, interface):
          pass

     def add_arbitrary_agent(self, new_agent, interface):
          tag = SecurityTag.objects.filter(interface, self)
          tag.add_agent(new_agent)
              
     def get_tags_on(self, resource) :
         context = resource.get_security_context()
         context_type = ContentType.objects.get_for_model(context)
         return SecurityTag.objects.filter(context_content_type=context_type, context_object_id=context.id)

     def setup_defaults(self,resource, owner, creator) :
         options = self.make_slider_options(resource,owner,creator)
         self.save_defaults(resource,owner,creator)
         interfaces = self.get_interfaces()
         s = interfaces['Viewer'].make_slider_for(resource,options,owner,0,creator)
         s = interfaces['Editor'].make_slider_for(resource,options,owner,2,creator)
         s = interfaces['Commentor'].make_slider_for(resource,options,owner,1,creator)
        



class SecurityTag(models.Model) :
    interface = models.CharField(max_length=100)
    security_context = models.ForeignKey(SecurityContext)  # revere is securitytag
    agents = models.ManyToManyField(Agent)
    def __str__(self) :
        return """(%s)Interface: %s, Contexte: %s, Agents: %s""" % (self.id, self.interface,self.context,self.agents)


