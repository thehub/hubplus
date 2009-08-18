from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, add_creator_interface
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents
from apps.hubspace_compatibility.models import TgGroup
from apps.plus_permissions.OurPost import OurPost
from django.db.models.signals import post_save
import datetime

content_type = TgGroup



import ipdb

from apps.plus_permissions.default_agents import get_or_create_root_location

# override object managers, filter, get, get_or_create
def get_or_create(group_name=None, display_name=None, place=None, level=None, user=None) :
    """get or create a group
    """
    # note : we can't use get_or_create for TgGroup, because the created date clause won't match on a different day
    # from the day the record was created.
    
    if not user:
        raise TypeError("We must have a user to create a group, since otherwise it will be inaccessible")
    if not place:
        place = get_or_create_root_location()

    xs = TgGroup.objects.filter(group_name=group_name)
    if len(xs) > 0 :
        group = xs[0]
        created = False
    else :
        created = True
        group = TgGroup(group_name=group_name, display_name=display_name, level=level, place=place)
        group.to_security_context()
        sec_context = group.get_security_context() 
        if level == 'member':

            admin_group, created = TgGroup.objects.get_or_create(
                group_name=group_name + "_hosts", 
                display_name=display_name + " Hosts", 
                level='host',
                place=place,
                user=user
                )
            sec_context.set_context_agent(group.get_ref())
            sec_context.set_context_admin(admin_group.get_ref())
            group.add_member(admin_group)
            group.add_member(user)
            group.save()
        elif level == 'host':
            sec_context.set_context_agent(group.get_ref())
            sec_context.set_context_admin(group.get_ref())
            group.add_member(user)
            group.save()
    return group, created

TgGroup.objects.get_or_create = get_or_create



 
# we need a special set_permissions interface which is only editable by the scontext_admin and determines who can set permissions or override them for an object. 

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



from apps.plus_permissions.models import add_type_to_interface_map

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


# ChildTypes are used to determine what types of objects can be created in this security context (and acquire security context from this). These are used when creating an explicit security context for an object of this type. 

child_types = [OurPost]
SetPossibleTypes(TgGroup, child_types)

# Add the create_* interfaces and sliders 
def add_create_interfaces() :
    for child in child_types :
        key = 'Create%s'%child.__class__.__name__
        TgGroupInterfaces[key] = add_creator_interface(child)
        SliderOptions['InterfaceOrder'].append(key)

add_create_interfaces()


# if the security context is in this agent, this set of slider_agents apply, irrespective of the type of resource they are
def get_slider_agents(scontext)  : 
    return [
            ('anonymous_group', get_anonymous_group()),
            ('all_members_group', get_all_members_group()), 
            ('context_agent', scontext.context_agent), 
            ('creator', get_creator_agent()),
            ('context_admin', scontext.context_admin)
           ]

SetSliderAgents(TgGroup, get_slider_agents)


# The agent must have a set of default levels for every type which can be created within it. Other objects don't need these as they will be copied from acquired security context according to the possible types available at the "lower" level. We have different AgentDefaults for different group types e.g. standard, public, or private.
AgentDefaults = {'public':
                     {'TgGroup':
                          {'defaults':
                               {'Viewer':'context_agent', 
                                'Editor':'creator',
                                'Invite':'context_agent'},
                           'constraints':
                               ['Viewer>=Editor', 'Invite>=ManageMembers', 'Join>=ManageMembers', 'ManageMembers<=$anonymous']
                           },
                      'OurPost':
                          { 'defaults' : {'Viewer':'context_agent',
                                          'Editor':'creator',
                                          'Commentor':'site_members'},
                            'constraints':['Viewer>=Editor']}
                      },
                 

                 'private':
                     {'TgGroup':
                          {'defaults':
                               {'Viewer':'context_agent', 
                                'Editor':'creator',
                                'Invite':'context_agent'},
                           'constraints':
                               ['Viewer>=Editor', 'Invite>=ManageMembers', 'Join>=ManageMembers', 'ManageMembers<=$anonymous']
                           },
                      'OurPost': 
                      {'defaults' : 
                       {'Viewer':'context_agent',
                        'Editor':'creator',
                        'Commentor':'site_members'},
                       'constraints':['Viewer>=Editor']}
                      }
                 }

SetAgentDefaults(TgGroup, AgentDefaults)


