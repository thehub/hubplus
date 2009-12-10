
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User, AnonymousUser
from apps.plus_groups.models import TgGroup
from django.db.transaction import commit_on_success

from apps.plus_permissions.site import Site

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



VisibleAgents = {}
def SetVisibleAgents(type, options):
     VisibleAgents[type] = options

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

VisibleTypes = {}
def SetVisibleTypes(type, options):
     VisibleTypes[type] = options

class TypeLabels(dict): 
    def __init__(self):
        dict.__init__(self)

    def __missing__(self, key):
        return key.__name__

typelabels = TypeLabels()

def SetTypeLabels(type, options):
     typelabels[type] = options

from apps.plus_permissions.default_agents import get_anonymous_group, get_admin_user, get_all_members_group, get_creator_agent, CreatorMarker
from apps.plus_permissions.exceptions import PlusPermissionsReadOnlyException, PlusPermissionsNoAccessException, NonExistentPermission, PlusPermissionAnonUserException


def get_selected_agent(sad, agent_defaults, type_name, interface_name) :
    try:
        return sad[agent_defaults[type_name]['defaults'][interface_name]]
    except KeyError:
        return sad[agent_defaults[type_name]['defaults']['Unknown']]



class SecurityContext(models.Model):
     """Target is the thing the context is associated with e.g. Group. 
     The thing that we will metaphorically put things "in".
     Context Agent is the 

     """

     def get_target(self):
         return self.target.all()[0].obj

     def get_slider_agent_dictionary(self) :
         slider_agents = SliderAgents[self.context_agent.obj.__class__](self)
         return dict(slider_agents)

     def get_my_type(self) :
         return self.get_target().__class__
     
     def set_up(self, permission_prototype='public', **kwargs):
         """XXX set from maps and create security tags         """
         # setting up security_tags

         my_type = self.get_my_type()
         self.context_agent.permission_prototype = permission_prototype
         agent_defaults = AgentDefaults[self.context_agent.obj.__class__][permission_prototype]

         sad = self.get_slider_agent_dictionary()

         types = [my_type] + PossibleTypes[my_type]
         for typ in types:
             for interface_name in get_interface_map(typ.__name__):
                 interface_str = '%s.%s' %(typ.__name__, interface_name)
                 self.setup_tag_from_defaults(interface_str, sad, agent_defaults)


     def switch_permission_prototype(self, permission_prototype) :
         # XXX refactor to eliminate redundancy with set_up
         my_type = self.get_my_type()
         self.context_agent.permission_prototype = permission_prototype
         agent_defaults = AgentDefaults[self.context_agent.obj.__class__][permission_prototype]

         sad = self.get_slider_agent_dictionary()
         types = [my_type] + PossibleTypes[my_type]
         for typ in types:
             for interface_name in get_interface_map(typ.__name__):
                 interface_str = '%s.%s' %(typ.__name__, interface_name)

                 # seems to create missing sliders (if new interfaces are added)
                 self.get_slider_level(interface_str)

                 
                 type_name, interface_name = interface_str.split('.')
                 selected_agent = get_selected_agent(sad, agent_defaults, type_name, interface_name)
                 self.move_slider(selected_agent, interface_str, skip_validation=True, no_user=True)


     def setup_tag_from_defaults(self, interface_str, sad, agent_defaults):
         typ, interface_name = interface_str.split('.')
         self.create_security_tag(interface_str)
         selected_agent = get_selected_agent(sad, agent_defaults, typ, interface_name)
         self.move_slider(selected_agent, interface_str, skip_validation=True, no_user=True)


     def is_agent(self, target):
         return ( isinstance(target.obj, User) or isinstance(target.obj, TgGroup) )
         # Maybe?  isinstance(target.obj, Site) ... 
         # at the moment we make Site acquire_from all_members_group's admin


     context_agent = models.ForeignKey('GenericReference', null=True, related_name="agent_scontexts")
     # The agent which this security context is associated with

     def set_context_agent(self, agent):
         if not self.is_agent(agent) :
             raise TypeError("Agent must be a user, a group or a site")
         self.context_agent = agent

     context_admin = models.ForeignKey('GenericReference', null=True, related_name="admin_scontexts") 
     # The admin which this security context is associated with

     def set_context_admin(self, admin):
         if not self.is_agent(admin) :
             raise TypeError("Admin must be a user of a group")
         self.context_admin = admin

         return self.context_admin
                    
     def create_security_tag(self, interface, agents=None):
         tag = SecurityTag(security_context=self, interface=interface)
         tag.save()
         
         if agents:
             tag.add_agents(agents)
         return tag
     
     def get_constraints(self, type_name):
         return AgentDefaults[self.context_agent.obj.__class__][self.context_agent.permission_prototype][type_name]['constraints']          
         
     def get_tags(self) :
         return SecurityTag.objects.filter(security_context=self)

     def get_tags_for_interface(self, interface):
         return SecurityTag.objects.filter(security_context=self, interface=interface)

     def get_interfaces(self):
         s = set([tag.interface for tag in self.get_tags()])
         return [x for x in s]

     def diagnose_interface(self, iface):
         print iface
         for t in self.get_tags_for_interface(iface):
             print t.security_context.context_agent.obj,
             for a in t.agents.all() :
                 print a.obj

     def diagnose(self, interface=None):
         if interface : self.diagnose_interface(interface)
         for i in self.get_interfaces():
             self.diagnose_interface(i)
             
     def get_slider_agents(self, visible_only=False):
         agents = SliderAgents[self.context_agent.obj.__class__](self)
         if visible_only:
             return [agent for agent in agents if agent[0] in VisibleAgents[self.context_agent.obj.__class__]]
         return agents

     def get_slider_agents_json(self, visible_only=False):
         return [{'agent_label':agent[0],
                  'agent_id':agent[1].obj.id,
                  'agent_class':agent[1].obj.__class__.__name__} for agent in self.get_slider_agents(visible_only)]


     def validate_constraints(self, type_name):
         slider_agents = self.get_slider_agents()
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
     def move_sliders(self, interface_level_map, type_name, user):
         """move multiple sliders at the same time for a particular type, raising an error if the final position violates constraints
         """
         for interface, agent in interface_level_map.iteritems():
             if interface.split('.')[0] == type_name:
                 self.move_slider(agent, interface, user, skip_validation=True)
         self.validate_constraints(type_name)
 
     def can_set_manage_permissions(self, interface, user):
         type_name, iface_name = interface.split('.')
         if iface_name == "ManagePermissions":
             if not has_access(agent=user, resource=self.context_agent.obj, interface=self.context_agent.obj.__class__.__name__ + '.SetManagePermissions') :
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

     def get_acquiring_types(self, my_type, already_seen=None):
         """at some point we may have to check for cycling here
         """
         if already_seen == None:
             already_seen = []
         try:
             poss_types = list(VisibleTypes[my_type])    #assumes we only use this for display - otherwise we would use PossibleTypes
         except KeyError:
             poss_types = []
         for typ in poss_types:
             if typ in already_seen:
                 continue
             already_seen.append(typ)
             return  poss_types + [typ for typ in self.get_acquiring_types(typ, already_seen) if typ not in poss_types]
         #if this_type:
         #    return [this_type]
         return []

     def get_all_sliders(self, my_type, user):
         types = self.get_acquiring_types(my_type)
         return [(typ.__name__, self.get_type_slider(typ, user), typelabels[typ]) for typ in types if has_access(user, self.get_target(), typ.__name__ + '.ManagePermissions')]

     def get_type_slider(self, typ, user):
         """get all the sliders associated with a particular type in this SecurityContext
         """
         type_name = typ.__name__
         constraints = self.get_constraints(type_name)
         interpreted_constraints = {}
         slider_agents = self.get_slider_agents()
         sad = dict(slider_agents)
         for constraint in constraints:
             arg1, arg2, op = interpret_constraint(constraint)
             if arg1.startswith('$'):
                 arg1 = serialize_agent(sad[arg1[1:]].obj)
                 interpreted_constraints.setdefault(arg2, [])
                 interpreted_constraints[arg2].append([stringify(reverse(op)), arg1])
             elif arg2.startswith('$'):
                 arg2 = serialize_agent(sad[arg2[1:]].obj)
                 interpreted_constraints.setdefault(arg1, [])
                 interpreted_constraints[arg1].append([stringify(op), arg2])
             else:
                 interpreted_constraints.setdefault(arg1, [])
                 interpreted_constraints[arg1].append([stringify(op), arg2])
                 interpreted_constraints.setdefault(arg2, [])
                 interpreted_constraints[arg2].append([stringify(reverse(op)), arg1])
         options = SliderOptions[typ]['InterfaceOrder']
         if 'ManagePermissions' in options:
             options = list(options) #copy the list so that we can remove the item *only* for this rendering
             if not has_access(agent=user, resource=self.context_agent.obj, interface=self.context_agent.obj.__class__.__name__ + '.SetManagePermissions'):
                 options.remove('ManagePermissions')
         interface_levels = [(interface, self.get_slider_level_json(type_name + '.' + interface)) for interface in options ]
         return {'constraints': interpreted_constraints,
                 'interface_levels': interface_levels}
         
     def get_slider_level_json(self, interface):
         level = self.get_slider_level(interface)
         return {'classname':level.__class__.__name__, 'id':level.id}

     def get_slider_level(self, interface):
         slider_agents = SliderAgents[self.context_agent.obj.__class__](self)
         try:
             tag = SecurityTag.objects.get(interface=interface, security_context=self)
         except SecurityTag.DoesNotExist:
             agent_defaults = AgentDefaults[self.context_agent.obj.__class__][self.context_agent.permission_prototype]
             sad = dict(slider_agents)
             self.setup_tag_from_defaults(interface, sad, agent_defaults)
             tag = SecurityTag.objects.get(interface=interface, security_context=self)

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
    class Meta:
        unique_together = (("content_type", "object_id"),)

    content_type = models.ForeignKey(ContentType, related_name='security_tag_agent') # this related name makes no sense, is it used anywhere or can we change it?
    object_id = models.PositiveIntegerField()
    obj = generic.GenericForeignKey()
    
    acquires_from = models.ForeignKey("GenericReference", related_name="acquirers", null=True)
    acquired_scontext = models.ForeignKey(SecurityContext, related_name="controlled", null=True)
    explicit_scontext = models.ForeignKey(SecurityContext, related_name="target", null=True, unique=True)

    #this should be null=True
    creator = models.ForeignKey(User, related_name='created_objects', null=True, default=get_admin_user())
    
    # at the moment, the permission_prototype will hold what family or broad class of permissions this falls 
    # into ... for example, groups are public, private, invite etc.
    # If there are only these, we can add a choice to this field, but I'm not 100% certain yet.
    permission_prototype = models.CharField(max_length=10, null=True)


    def delete(self) :
        # remove the generic reference
        # try not to call this directly, but via deleting a group etc. (which we'll wrap in a transaction)

        # remove tags                                                                                                    
        from apps.plus_tags.models import TagItem, tag_item_delete
        for ti in TagItem.objects.filter(ref=self) :
            tag_item_delete(ti)

        super(GenericReference,self).delete()

        

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

def serialize_agent(arg2):
    is_agent(arg2)
    return "$" + arg2.__class__.__name__ + "-" + str(arg2.id)

def stringify(op):
    if op == operator.ge:
        return '>='
    if op == operator.le:
        return '<='
    if op == operator.lt:
        return '<'
    if op == operator.gt:
        return '>'

def reverse(op):
    if op == operator.ge:
        return operator.le
    if op == operator.le:
        return operator.ge
    if op == operator.gt:
        return operator.lt
    if op == operator.lt:
        return operator.gt


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
        new_st.add_agents(self.agents.all())
            

    def __str__(self) :
        return """(%s)Interface: %s, Contexte: %s, Agents: %s""" % (self.id, self.interface,self.security_context, self.agents)




def secure_filter(agent, objects, interface):
    """ Don't do 1000 requests if we have 1000 objects in a list and want to know which ones we can view or search.
    user --> agents --> security context --> security tag <-- interface
    resources --> security_contexts --> security tags <-- interface
    """
    pass


def has_access(agent, resource, interface, sec_context=None) :
    """Does the agent have access to this interface in this resource. All the special casing below will make it hard to refactor this method and for instance make it work for a whole lot of objects
    """
    
    # make sure we've stripped agent from any SecureWrappers
    if agent.__class__.__name__ == "SecureWrapper":
        agent = agent.get_inner()
 

    if not sec_context:
        # make sure we've stripped resource from any SecureWrappers
        if resource.__class__.__name__ == "SecureWrapper":
            resource = resource.get_inner()


        context = resource.get_security_context()
    else:
        context = sec_context

    # which agents have access?

    if not SecurityTag.objects.filter(interface=interface, security_context=context):
        #lets create it if it is in defaults for the type -- this allows adding new interfaces to the type at runtime
        typ = resource.__class__
        interface_name = interface.split('.')[1]
        if interface_name in get_interface_map(typ.__name__):

            agent_defaults = AgentDefaults[context.context_agent.obj.__class__][context.context_agent.permission_prototype]
            slider_agents = SliderAgents[context.context_agent.obj.__class__](context)
            sad = dict(slider_agents)
            context.setup_tag_from_defaults(interface, sad, agent_defaults)

    allowed_agents = SecurityTag.objects.get(interface=interface,
                                             security_context=context).agents
    

    # probably should memcache both allowed agents (per .View interface) and 
    # agents held per user to allow many queries very quickly. 
    allowed_agents = set([a.obj for a in allowed_agents.all()])
    

    if get_anonymous_group() in allowed_agents: 
        # in other words, if this resource is matched with anyone, we don't have to test 
        #that user is in the "anyone" group
        return True

    if resource:
        if get_creator_agent().obj in allowed_agents :
            actual_creator = resource.get_ref().creator
            if agent == actual_creator:
                return True

    if agent.__class__ == AnonymousUser :
        # we clearly shouldn't be seeing this - sure but is this a security issue - t.s.
        return False

    agents_held = agent.get_enclosure_set()
    if allowed_agents.intersection(agents_held):
        return True

    print "has_access fails for %s, %s, %s, %s" %(interface, resource, context.context_agent.obj, agent)
    return False

