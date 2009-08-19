from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User
from apps.hubspace_compatibility.models import TgGroup

import pickle
import simplejson

import datetime


type_interfaces_map = {}  

def get_interface_map(cls):
    if not isinstance(cls, basestring):
        cls = cls.__name__
    return type_interfaces_map.get(cls, {})

def add_type_to_interface_map(cls, interfaces):
    print "adding %s to %s in interface map" % (','.join(interfaces),cls.__name__)
    type_interfaces_map[cls.__name__] = {}
    add_interfaces_to_type(cls, interfaces)
        
def add_interfaces_to_type(cls, interfaces):
    if not isinstance(interfaces, dict):
        raise TypeError
    type_interfaces = type_interfaces_map[cls.__name__]
    for label, interface in interfaces.iteritems():
        if label not in type_interfaces:
            type_interfaces[label] = interface
        else:
            raise "Interface "+ label  +"was not added to "+ `cls` +" because an interface of that name already exists"



SliderOptions = {}
def SetSliderOptions(type, options):
    SliderOptions[type] = options

SliderAgents = {}
def SetSliderAgents(type, options) :
     SliderAgents[type] = options

AgentSecurityContext = {}
def SetAgentSecurityContext(type, options):
     AgentSecurityContext[type] = options

AgentDefaults = {}
def SetAgentDefaults(type, options):
     AgentDefaults[type] = options

PossibleTypes = {}
def SetPossibleTypes(type, options):
     PossibleTypes[type] = options

from apps.plus_permissions.default_agents import get_anonymous_group, get_admin_user, get_all_members_group, get_creator_agent

class SecurityContext(models.Model):
     """Target is the thing the context is associated with e.g. Group. 
     The thing that we will metaphorically put things "in".
     Context Agent is the 

     """
     def get_target(self):
         return self.target.all()[0].obj
         
     def set_up(self):
         """XXX set from maps and create security tags
         """
         
         # setting up security_tags

         my_type = self.get_target().__class__
         
         agent_defaults = AgentDefaults[TgGroup]['public']

         self.slider_agents = SliderAgents[my_type](self)
         self.slider_agents.reverse()
         sad = dict(self.slider_agents)

         types = [my_type] + PossibleTypes[my_type]
         for typ in types:
             for interface_name in get_interface_map(typ.__name__):
                 interface_str = '%s.%s' %(typ.__name__, interface_name)
                 self.create_security_tag(interface_str)
                 selected_agent = sad[agent_defaults[typ.__name__]['defaults'][interface_name]]

                 self.move_slider(selected_agent, interface_str)
                   

          

     context_agent = models.ForeignKey('GenericReference', null=True, related_name="agent_scontexts")
     # The agent which this security context is associated with

     def set_context_agent(self, agent):
          if not isinstance(agent.obj, TgGroup) and not isinstance(agent.obj, User):
               raise TypeError("Agent must be a user of a group")
          self.context_agent = agent

     def get_context_agent(self):
          if self.context_agent:
               return self.context_agent
          context_agent_ref = self.target
          while not isinstance(context_agent_ref.obj, User) and not isinstance(context_agent_ref.obj, TgGroup):
               context_agent_ref = context_agent_ref.acquires_from
          self.context_agent = context_agent_ref.obj
          return self.context_agent

     context_admin = models.ForeignKey('GenericReference', null=True, related_name="admin_scontexts") 
     # The admin which this security context is associated with

     def set_context_admin(self, admin):
          if not isinstance(admin.obj, TgGroup) and not isinstance(admin.obj, User):
               raise TypeError("Admin must be a user of a group")
          self.context_admin = admin

     def get_context_admin(self):
          if self.context_admin:
               return self.context_admin
          context_admin_ref = self.target
          while not isinstance(context_admin_ref.obj, User) and not isinstance(context_admin_ref.obj, TgGroup):
               context_admin_ref = context_admin_ref.acquires_from
          self.context_admin = context_admin_ref.obj
          return self.context_admin

     contraints = models.TextField()     # {type: [contstraints]}  e.g. {wiki:['editor<viewer']}
                    
     def create_security_tag(self, interface, agents=None):
         tag = SecurityTag(security_context=self, interface=interface)
         tag.save()
         if agents:
             tag.add_agents(agents)
         return tag
     
     def move_slider(self, new_agent, interface):
          slider_agents = [t[1] for t in self.slider_agents]
          if new_agent in slider_agents:
               tag = SecurityTag.objects.get(interface=interface, security_context=self)
               split = slider_agents.index(new_agent) + 1
               adds = slider_agents[:split]
               removes = slider_agents[split:]
               tag.remove_agents(removes)
               tag.add_agents(adds)


     def get_slider_level(self, interface):
          tag = SecurityTag.objects.get(interface=interface, security_context=self)
          for label, agent in self.slider_agents:
               highest = agent
               if agent not in tag.agents:
                    break
          return highest

     def add_arbitrary_agent(self, new_agent, interface):
          tag = SecurityTag.objects.get(interface, self)
          tag.add_agents([new_agent])

     def remove_arbitrary_agent(self, old_agent, interface):
          tag = SecurityTag.objects.get(interface, self)
          tag.remove_agents([old_agent])

              
        


class GenericReference(models.Model):
    content_type = models.ForeignKey(ContentType, related_name='security_tag_agent')
    object_id = models.PositiveIntegerField()
    obj = generic.GenericForeignKey()
    
    acquires_from = models.ForeignKey("GenericReference", related_name="acquirers", null=True)
    acquired_scontext = models.ForeignKey(SecurityContext, related_name="controlled", null=True)
    explicit_scontext = models.ForeignKey(SecurityContext, related_name="target", null=True, unique=True)

    creator = models.ForeignKey(User, related_name='created_objects', null=True)
    

def ref(agent) :
    # if we're sent ordinary agent (group etc.) get the ref, if we've already got a ref, just return it
    if agent.__class__ != GenericReference : 
        return agent.get_ref()
    return agent

class SecurityTag(models.Model) :
    interface = models.CharField(max_length=100)
    security_context = models.ForeignKey(SecurityContext)  # revere is securitytag
    agents = models.ManyToManyField(GenericReference)

    class Meta:
        unique_together = (("interface", "security_context"),)

    def add_agents(self, agents=None):
         """pass in a list of users and groups
         """
         db_agents = self.agents
         agents = [ref(agent) for agent in agents if agent not in db_agents.all()]
         self.agents.add(*agents)
         self.save()

    def remove_agents(self, agents=None):
         """pass in a list of users and groups
         """
         db_agents = self.agents
         agents = [agent.get_ref() for agent in agents if agent in db_agents.all()]
         self.agents.remove(*agents)
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
    try :
         allowed_agents = SecurityTag.objects.get(interface=interface,
                                                  security_context=context).agents
    except Exception, e:
         print e
         raise e

    # probably should memcache both allowed agents (per .View interface) and agents held per user to allow many queries very quickly. e.g. to only return the searc
     
    allowed_agents = set([a.obj for a in allowed_agents])
    
    if self.anonymous_group in allowed_agents: 
        # in other words, if this resource is matched with anyone, we don't have to test 
        #that user is in the "anyone" group
        return True

    if get_creator_agent() in allowed_agents:
        actual_creator = resource.get_ref().creator
        if agent == actual_creator:
            return True
          
    agents_held = agent.get_enclosure_set()
    if allowed_agents.intersection(agents_held):
        return True

    return False



