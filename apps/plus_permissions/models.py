from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User
from apps.hubspace_compatibility.models import TgGroup
from django.db.transaction import commit_on_success

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

from apps.plus_permissions.default_agents import get_anonymous_group, get_admin_user, get_all_members_group, get_creator_agent, CreatorMarker
from apps.plus_permissions.exceptions import PlusPermissionsReadOnlyException, PlusPermissionsNoAccessException, NonExistentPermission

class SecurityContext(models.Model):
     """Target is the thing the context is associated with e.g. Group. 
     The thing that we will metaphorically put things "in".
     Context Agent is the 

     """

     def get_target(self):
         return self.target.all()[0].obj
         
     def set_up(self,**kwargs):
         """XXX set from maps and create security tags
         """
         
         # setting up security_tags
         my_type = self.get_target().__class__         
         agent_defaults = AgentDefaults[self.context_agent.obj.__class__]['public']

         slider_agents = SliderAgents[self.context_agent.obj.__class__](self)

         sad = dict(slider_agents)

         types = [my_type] + PossibleTypes[my_type]
         for typ in types:
             for interface_name in get_interface_map(typ.__name__):
                 interface_str = '%s.%s' %(typ.__name__, interface_name)
                 self.create_security_tag(interface_str)
                 selected_agent = sad[agent_defaults[typ.__name__]['defaults'][interface_name]]
                 self.move_slider(selected_agent, interface_str, skip_validation=True, no_user=True)
         

         tag = self.create_security_tag(interface='SetPermissionManager',security_context=self)
         tag.save()
         tag.add_agents([self.context_admin])

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
                    
     def create_security_tag(self, interface, agents=None):
         #print "creating security tag", self, interface, agents
         tag = SecurityTag(security_context=self, interface=interface)
         tag.save()
         
         if agents:
             tag.add_agents(agents)
         return tag
     
     def get_constraints(self, type_name):
         return AgentDefaults[self.context_agent.obj.__class__]['public'][type_name]['constraints']          

     def get_tags(self) :
         return SecurityTag.objects.filter(security_context=self)

     def validate_constraints(self, type_name):
         slider_agents = SliderAgents[self.context_agent.obj.__class__](self)
         slider_agents.reverse()
         slider_agents_names = [t[0] for t in slider_agents]
         slider_agents = [t[1] for t in slider_agents]
         for constraint in self.get_constraints(type_name):
             iface_or_agent_1, iface_or_agent_2, op = interpret_constraint(constraint)
             if iface_or_agent_1.startswith('$'):
                 index_1 = slider_agents_names.index(iface_or_agent_1[1:])
             else:
                 index_1 = slider_agents.index(self.get_slider_level(type_name + '.' + iface_or_agent_1).get_ref())
             if iface_or_agent_2.startswith('$'):
                 index_2 = slider_agents_names.index(iface_or_agent_2[1:])
             else:
                 index_2 = slider_agents.index(self.get_slider_level(type_name + '.' + iface_or_agent_2).get_ref())
             if not op(index_1, index_2):
                 raise InvalidSliderConfiguration
         return True

     @commit_on_success
     def move_sliders(self, interface_level_map, type_name):
         """move multiple sliders at the same time for a particular type, raising an error if the final position violates constraints
         """
         for interface, agent in interface_level_map.iteritems():
             if interface.split('.')[0] == type_name:
                 self.move_slider(agent, interface, skip_validation=True)
         self.validate_constraints(type_name)
 
     def can_set_manage_permissions(interface, user):
         type_name, iface_name = interface.split('.')
         if iface_name == "ManagePermissions":
             if not has_access(agent=user, security_context=self, interface='SetManagePermissions') :
                 raise PlusPermissionsNoAccessException(None,None,"You can't set permission manager slider if you aren't the group admin")
        
        
     def move_slider(self, new_agent, interface, user=None, skip_validation=False, no_user=False):
         """skip_validation is necessary on setup because some of the SecurityTags won't yet exist. Also when we move multiple sliders at the same time we should skip validation in the same way.
         """
         
         if user:
             self.can_set_manage_permissions(interface, user)
         else:
             if not no_user:
                 raise NotAnAgent

         type_name, iface_name = interface.split('.')
         try:
             new_agent.obj
         except:
             if is_agent(new_agent):
                 new_agent = new_agent.get_ref()
             else:
                 raise NotAnAgent
         slider_agents = SliderAgents[self.context_agent.obj.__class__](self)
         slider_agents.reverse()
         slider_agents = [t[1] for t in slider_agents]
         if new_agent in slider_agents:
             tag = SecurityTag.objects.get(interface=interface, security_context=self)
             split = slider_agents.index(new_agent) + 1
             adds = slider_agents[:split]
             removes = slider_agents[split:]
             tag.remove_agents(removes)
             tag.add_agents(adds)
         if not skip_validation:
             self.validate_constraints(type_name)

     def get_all_sliders(self, my_type, user):
         types = [my_type] + PossibleTypes[my_type]
         return [(type.__name__, self.get_type_slider(type.__name__, user)) for type in types]

     def get_type_slider(self, type_name, user):
         """get all the sliders associated with a particular type in this SecurityContext
         """
         constraints = self.get_constraints(type_name)
         options = SliderOptions[type]['InterfaceOrder']
         try :
             self.can_set_manage_permissions(interface, user)
         except PlusPermissionsNoAccessException :
             if 'ManagePermissions' in options :
                 options.remove('ManagePermissions')
         interface_levels = [(interface, self.get_slider_level(type_name + '.' + interface)) for interface in options ]
         return {'constraints': constraints,
                 'interface_levels': interface_levels}
         
     def get_slider_level(self, interface):
         tag = SecurityTag.objects.get(interface=interface, security_context=self)
         slider_agents = SliderAgents[self.context_agent.obj.__class__](self)
         slider_agents.reverse()
         for label, agent in slider_agents:
             if agent not in tag.agents.all():
                 break
             highest = agent
         return highest.obj
     
     def add_arbitrary_agent(self, new_agent, interface, user):
         self.can_set_manage_permissions(interface, user)
         tag = SecurityTag.objects.get(interface=interface, security_context=self)
         tag.add_agents([new_agent.get_ref()])

     def remove_arbitrary_agent(self, old_agent, interface, user):
         self.can_set_manage_permissions(interface, user)
         tag = SecurityTag.objects.get(interface=interface, security_context=self)
         tag.remove_agents([old_agent.get_ref()])

              


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


class NotAnAgent(Exception):
    pass

def is_agent(obj):
    if isinstance(obj, User) or isinstance(obj, TgGroup) or isinstance(obj, CreatorMarker):
        return True
    raise NotAnAgent


class InvalidSliderConfiguration(Exception):
    pass

import operator

def interpret_constraint(constraint):
    if '>=' in constraint:
        arg1, arg2 = constraint.split('>=')
        return (arg1.strip(), arg2.strip(), operator.ge)
    if '<=' in constraint:
        arg1, arg2 = constraint.split('<=')
        return (arg1.strip(), arg2.strip(), operator.le)
    if '<' in constraint:
        arg1, arg2 = constraint.split('<')
        return (arg1.strip(), arg2.strip(), operator.lt)
    if '>' in constraint:
        arg1, arg2 = constraint.split('>')
        return (arg1.strip(), arg2.strip(), operator.gt)

class SecurityTag(models.Model) :
    interface = models.CharField(max_length=100)
    security_context = models.ForeignKey(SecurityContext)  # reverse is securitytag
    agents = models.ManyToManyField(GenericReference)

    class Meta:
        unique_together = (("interface", "security_context"),)

    def add_agents(self, agents=None):
         """pass in a list of users and groups
         """
         
         db_agents = self.agents
         adds = []
         for agent in agents:
             if agent not in db_agents.all():
                 if is_agent(agent.obj):
                     adds.append(agent)
         self.agents.add(*adds)
         self.save()

    def remove_agents(self, agents=None):
         """pass in a list of users and groups
         """
         db_agents = self.agents
         removes = []
         for agent in agents: 
             if agent in db_agents.all():
                 if is_agent(agent.obj):
                     removes.append(agent)
         self.agents.remove(*removes)
         self.save()

    def clone_for_context(self, other_context) :
        new_st = SecurityTag(interface=self.interface, security_context=other_context)
        new_st.save()
        new_st.add_agents(self.agents)
            

    def __str__(self) :
        return """(%s)Interface: %s, Contexte: %s, Agents: %s""" % (self.id, self.interface,self.security_context, self.agents)



def has_access(agent, resource, interface) :
    """Does the agent have access to this interface in this resource
    """
        
    # we're always interested in the security_context of this resource
    context = resource.get_security_context()
    context_type = ContentType.objects.get_for_model(context)

    # which agents have access?

    if SecurityTag.objects.filter(interface=interface,security_context=context) :
        allowed_agents = SecurityTag.objects.get(interface=interface,
                                                 security_context=context).agents

    else :

        # force the exception again
        allowed_agents = SecurityTag.objects.get(interface=interface,
                                                security_context=context).agents
    

    # probably should memcache both allowed agents (per .View interface) and 
    # agents held per user to allow many queries very quickly. e.g. to only return the searc
     
    allowed_agents = set([a.obj for a in allowed_agents.all()])
    
    if get_anonymous_group in allowed_agents: 
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



