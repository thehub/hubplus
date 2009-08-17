from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty
from apps.plus_permissions.models import SetSliderOptions, SetAgentSecurityContext, SetAgentDefaults, SetPossibleTypes
from apps.hubspace_compatibility.models import TgGroup
from apps.plus_permissions.OurPost import OurPost
from django.db.models.signals import post_save
import datetime
content_type = TgGroup

import ipdb

# override object managers, filter, get, get_or_create
from apps.plus_permissions.permissionable import get_or_create_root_location

def get_or_create(group_name=None, display_name=None, place=None, level=None) :
    """get or create a group
    """
    # note : we can't use get_or_create for TgGroup, because the created date clause won't match on a different day                                     
    # from the day the record was created.                                                                                                              
    if not place:
        place = get_or_create_root_location()
    xs = TgGroup.objects.filter(group_name=group_name)
    if len(xs) > 0 :
        group = xs[0]
    else :
        group = TgGroup(group_name=group_name, display_name=display_name, level=level, place=place)
        group.to_security_context()
        if level == 'member':
            admin = TgGroup.objects.get_or_create(
                group_name=group_name + "_hosts", 
                display_name=display_name + " Hosts", 
                level='host',
                place=place,
                )
            sec_context = get_security_context(group)  #.get_ref().explicit_scontext
            sec_context.set_context_agent(group.get_ref())
            sec_context.set_context_admin(admin.get_ref())
            group.add_member(admin)
            
        elif 'host':
            group.get_ref().explicit_scontext.set_context_agent(group.get_ref())
            sec_context.set_context_agent(group.get_ref())
            sec_context.set_context_admin(group.get_ref())
    return group

TgGroup.objects.get_or_create = get_or_create
#we need to create a security context and an admin group here. We should overrider the manger method on TgGroup 
 

#class TgGroupManager(model.managers):
#    super()
 #   self.get_or_create = get_or_create_group

#TgGroup.objects = TgGroupManager

#       
class TgGroupViewer: 

    pk = InterfaceReadProperty
    about = InterfaceReadProperty
    location = InterfaceReadProperty
    website = InterfaceReadProperty
    display_name = InterfaceReadProperty
    groupextras = InterfaceReadProperty

    apply = InterfaceCallProperty
    leave = InterfaceCallProperty


class TgGroupEditor: 
    pk = InterfaceReadProperty
    about = InterfaceWriteProperty
    location = InterfaceWriteProperty
    website = InterfaceWriteProperty
    display_name = InterfaceWriteProperty
    

class TgGroupJoin:
    pk = InterfaceReadProperty
    join = InterfaceCallProperty

class TgGroupInviteMember:
    pk = InterfaceReadProperty
    invite_member = InterfaceCallProperty

class TgGroupManageMembers:
    pk = InterfaceReadProperty
    add_member = InterfaceCallProperty
    accept_member = InterfaceCallProperty
    remove_member = InterfaceCallProperty

from apps.plus_permissions.interfaces import add_type_to_interface_map

TgGroupInterfaces = {'Viewer': TgGroupViewer,
                     'Editor': TgGroupEditor,
                     'Invite': TgGroupInviteMember,
                     'ManageMembers': TgGroupManageMembers,
                     'Join': TgGroupInviteMember}

add_type_to_interface_map(TgGroup, TgGroupInterfaces)


# use InterfaceOrder to draw the slider and constraints, these are used in rendering the sliders and in validating the results
# these exist on a per type basis and are globals for their type.
# they don't need to be stored in the db
SliderOptions = {'InterfaceOrder':['Viewer', 'Editor', 'Invite', 'Join', 'ManageMembers']}

SetSliderOptions(TgGroup, SliderOptions)  
# if the security context is in this agent, this set of slider_agents apply irrespective of the type they or applied to and the security context. Constraints are also specified here since we needs to know the format of "slider_agents" in order to be able to specify an absolute constraint on level for a particular interface.
AgentSecurityContext = {'slider_agents': ['$anonymous_group',
                                          '$all_members_group',
                                          '$context_agent',
                                          '$creator',
                                          '$context_agent_admin'],
                        'constraints':['*.Viewer>=*.Editor', 'Group.Invite>=Group.ManageMembers', 'Group.Join>=ManageMembers', 'ManageMembers<=3']
                        }

SetAgentSecurityContext(TgGroup, AgentSecurityContext)

# The agent must have a set of default levels for every type which can be created within it. Other objects don't need these as they will be copied from acquired security context according to the possible types available at the "lower" level. We have different AgentDefaults for different group types e.g. standard, public, or private.
AgentDefaults = {'public':{'TgGroup':{'Viewer':'$context_agent', 
                                      'Editor':'$creator',
                                      'Invite':'$context_agent'},
                           'OurPost':{'Viewer':'$context_agent',
                                      'Editor':'$creator'}
                           },
                 'private':{'TgGroup':{'Viewer':'$context_agent', 
                                       'Editor':'$creator',
                                       'Invite':'$context_agent'},
                            'OurPost':{'Viewer':'$context_agent',
                                       'Editor':'$creator'}
                            }           
                 }

SetAgentDefaults(TgGroup, AgentDefaults)
# PossibleTypes are used to determine what types of objects can be created in this security context (and acquire security context from this). These are used when creating an explicit security context for an object of this type. 
PossibleTypes = [OurPost]
SetPossibleTypes(TgGroup, PossibleTypes)
# we need a special set_permissions interface which is only editable by the scontext_admin and determines who can set permissions or override them for an object. 
