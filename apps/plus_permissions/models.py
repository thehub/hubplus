from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User
from apps.hubspace_compatibility.models import TgGroup

import pickle
import simplejson

import datetime

SliderOptions = {}
def SetSliderOptions(type, options):
     SliderOptions[type] = options

AgentSecurityContext = {}
def SetAgentSecurityContext(type, options):
     AgentSecurityContext[type] = options

AgentDefaults = {}
def SetAgentDefaults(type, options):
     AgentDefaults[type] = options

PossibleTypes = {}
def SetPossibleTypes(type, options):
     PossibleTypes = options


from apps.plus_permissions.default_agents import get_anonymous_group, get_admin_user, get_all_members_group

class SecurityContext(models.Model):
     """Target is the thing the context is associated with e.g. Group. The thing that we will metaphorically put things "in".
     Context Agent is the 

     """


     def set_up(self):
         """XXX set from maps and create security tags
         """
         for type in json_to_context:
              for interface in type:
                   tag = SecurityTag.get_or_create(interface, self)
                   self.add_default_agents(tag)
         self.set_context_agent()

     #def add_default_agents(self, tag):
     #     pass

     context_agent = models.ForeignKey('GenericReference', null=True, related_name="agent_scontexts")
     # The agent which this security context is associated with

     def set_context_agent(self, agent):
          if not isinstance(agent.obj, TgGroup) and not isinstance(agent.obj, User):
               raise TypeError("Agent must be a user of a group")
          self.context_agent = agent

     context_admin = models.ForeignKey('GenericReference', null=True, related_name="admin_scontexts") 
     # The admin which this security context is associated with

     def set_context_admin(self, admin):
          if not isinstance(admin.obj, TgGroup) and not isinstance(admin.obj, User):
               raise TypeError("Admin must be a user of a group")
          self.context_admin = admin


     def get_creator(self):
          return self.target.creator
               
     def get_context_agent(self):
          if self.context_agent:
               return self.context_agent
          context_agent_ref = self.target
          while not isinstance(context_agent_ref.obj, User) and not isinstance(context_agent_ref.obj, TgGroup):
               context_agent_ref = context_agent_ref.acquires_from
          self.context_agent = context_agent_ref.obj
          return self.context_agent

     def get_context_admin(self):
          if self.context_admin:
               return self.context_admin
          context_admin_ref = self.target
          while not isinstance(context_admin_ref.obj, User) and not isinstance(context_admin_ref.obj, TgGroup):
               context_admin_ref = context_admin_ref.acquires_from
          self.context_admin = context_admin_ref.obj
          return self.context_admin



     possible_types = models.TextField()
     slider_agents = models.TextField()  # order actually matters here
     contraints = models.TextField()     # {type: [contstraints]}  e.g. {wiki:['editor<viewer']}
     defaults  = models.TextField()      #{ type: [{interface:default_group},{interface:default_group}}
                    
     def create_security_tag(self, interface, agents) :
         # agents here is a list of something like User or TgGroup, NOT an Agent
          tag = SecurityTag(security_context=self, interface=interface)
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
        


class GenericReference(models.Model):
    content_type = models.ForeignKey(ContentType, related_name='security_tag_agent')
    object_id = models.PositiveIntegerField()
    obj = generic.GenericForeignKey()
    
    acquires_from = models.ForeignKey("GenericReference", related_name="acquirers", null=True)
    acquired_scontext = models.ForeignKey(SecurityContext, related_name="controlled", null=True)
    explicit_scontext = models.ForeignKey(SecurityContext, related_name="target", null=True, unique=True)

    creator = models.ForeignKey(User, related_name='created_objects', null=True)


class SecurityTag(models.Model) :
    interface = models.CharField(max_length=100)
    security_context = models.ForeignKey(SecurityContext)  # revere is securitytag
    agents = models.ManyToManyField(GenericReference)

    def add_agents(self, agents=None):
         """pass in a list of users and groups
         """
         for agent in agents :
              if agent.get_ref() not in self.agents:
                   self.agents.add(agent.get_ref())
         self.save()

    def remove_agents(self, agents=None):
         """pass in a list of users and groups
         """
         for agent in agents:
              if agent.get_ref() in self.agents():
                   self.agents.remove(agent.get_ref())
         self.save()

    def __str__(self) :
        return """(%s)Interface: %s, Contexte: %s, Agents: %s""" % (self.id, self.interface,self.context,self.agents)


def has_access(agent, resource, interface) :
    """Does the agent have access to this interface in this resource
    """
        
    # we're always interested in the security_context of this resource
    context = resource.get_security_context()
    context_type = ContentType.objects.get_for_model(context)

    # which agents have access?
    allowed_agents = GenericReference.objects.filter(securitytag__interface=interface,
                                                     securitytag__context_content_type=context_type,
                                                     securitytag__context_object_id=context.id)
    # probably should memcache both allowed agents (per .View interface) and agents held per user to allow many queries very quickly. e.g. to only return the searc
     
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
        
