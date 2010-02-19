from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, secure_wrap
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents, SetVisibleAgents, SetVisibleTypes, PossibleTypes, SetTypeLabels

from apps.plus_permissions.default_agents import get_all_members_group, get_anonymous_group, get_creator_agent

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from apps.profiles.models import Profile, HostInfo
from apps.plus_links.models import Link

import datetime
from copy import deepcopy
from apps.plus_lib.dict_tools import overlay
# We need our own get_or_create

from apps.plus_groups.models import User

def create_user(user_name, email_address, password='dummy', permission_prototype='public') :
    """create a User
    """

    if User.objects.filter(username=user_name).count() < 0 :
        user = User.objects.get(username=user_name)
    else :

        user = User(username=user_name, password=password, email=email_address)
        user.email_address=email_address
        user.user_name = user_name
        user.save()
        
        user_post_create(user)

        from apps.synced import post_user_create
        post_user_create.send(sender=user,user=user)

    return user

def user_post_create(user, permission_prototype='public') :
    
    user.save() # ensures our post_save signal is fired to create gen_ref, even if we came via syncer
    setup_user_security(user, permission_prototype)

    user.create_Profile(user,user=user)
    user.create_HostInfo(user,user=user)

    get_all_members_group().add_member(user)
    return user

def setup_user_security(user, permission_prototype):
    user.to_security_context()
    sec_context = user.get_security_context()
                    
    sec_context.set_context_agent(user.get_ref())
    sec_context.set_context_admin(get_all_members_group().get_admin_group().get_ref())
    sec_context.save()
        
    sec_context.set_up(permission_prototype)

    ref = user.get_ref()
    ref.creator = user
    ref.permission_prototype = permission_prototype
    ref.save()


content_type = User

# we need a special set_permissions interface which is only editable by the scontext_admin and determines who can set permissions or override them for an object. 


from apps.plus_permissions.models import add_type_to_interface_map

class UserViewer:
    pk = InterfaceReadProperty
    username = InterfaceReadProperty
    get_profile = InterfaceCallProperty
    get_display_name = InterfaceCallProperty
    display_name = InterfaceReadProperty 
    is_site_admin = InterfaceCallProperty
    hubs = InterfaceCallProperty

class UserEditor:
    preferably_pre_save = InterfaceCallProperty
    post_save = InterfaceCallProperty
    save = InterfaceCallProperty

class SetManagePermissions:
    pass


UserInterfaces = {
    'Viewer':UserViewer,
    'SetManagePermissions':SetManagePermissions,
    'Editor':UserEditor,

    }

add_type_to_interface_map(User, UserInterfaces)


# use InterfaceOrder to draw the slider and constraints, these are used in rendering the sliders and in validating the results
# these exist on a per type basis and are globals for their type.
# they don't need to be stored in the db
SliderOptions = {'InterfaceOrder':[], 'InterfaceLabels':{}}
SetSliderOptions(User, SliderOptions) 


# if the security context is in this agent, this set of slider_agents apply, irrespective of the type of resource they are
def get_slider_agents(scontext)  : 
    return [
            ('anonymous_group', get_anonymous_group().get_ref()),
            ('all_members_group', get_all_members_group().get_ref()), 
            ('context_agent', scontext.context_agent), 
            ('context_admin', scontext.context_admin)
           ]



def visible_agents():
    return ['anonymous_group', 'all_members_group', 'context_agent']
SetVisibleAgents(User, visible_agents())

SetSliderAgents(User, get_slider_agents)


# ChildTypes are used to determine what types of objects can be created in this security context (and acquire security context from this). These are used when creating an explicit security context for an object of this type. 



child_types = [Profile, HostInfo]
# ChildTypes are used to determine what types of objects can be created in this security context (and acquire security context from this). These are used when creating an explicit security context for an object of this type.

if User not in PossibleTypes:
    child_types = [Profile, HostInfo, Link]
    SetPossibleTypes(User, child_types)
    SetVisibleTypes(content_type, [Profile, HostInfo])
    SetTypeLabels(content_type, 'User')


# The agent must have a set of default levels for every type which can be created within it. Other objects don't need these as they will be copied from acquired security context according to the possible types available at the "lower" level. We have different AgentDefaults for different group types e.g. standard, public, or private.

#constraints - note that "higher" means wider access. Therefore if "anonymous can't edit" we must set that Editor<$anonymous OR if Editor functionality can't be given to a wider group than Viewer then we must set Editor < Viewer.

def setup_defaults():
    public_defaults = {'User':
                           {'defaults': 
                               {'Viewer': 'anonymous_group',
                                'Editor': 'context_admin',
                                 'SetManagePermissions': 'context_admin',
                                 'ManagePermissions':'context_agent',
                                 'CreateLink': 'context_admin',
                                 'Unknown': 'context_agent'
                                 },                           
                            'constraints':
                                []
                            },
                       'Profile':
                           {'defaults':
                                {'Viewer': 'anonymous_group',
                                 'Editor': 'context_agent',
                                 'EmailAddressViewer' : 'all_members_group',
                                 'HomeViewer' : 'all_members_group',
                                    'WorkViewer' : 'all_members_group',
                                    'MobileViewer' : 'all_members_group',
                                    'FaxViewer' : 'all_members_group',
                                    'AddressViewer' : 'all_memebers_group',
                                    'SkypeViewer' : 'all_members_group',
                                    'SipViewer' : 'all_members_group',
                                    'ManagePermissions':'context_agent',
                                    'Unknown' : 'context_agent',
                                    },
                               'constraints':['Viewer>=Editor', 'Viewer>$context_agent', 'Editor<$anonymous_group']
                               },
                          'Link': 
                              {'defaults': {'Viewer':'all_members_group',
                                            'Manager':'context_agent',
                                            'ManagePermissions':'context_agent',
                                            'Unknown' : 'context_agent'},
                               'constraints':['Viewer>=Manager']
                               },
                          'HostInfo':
                              {'defaults': {'Viewer':'context_agent',
                                            'Editor':'context_agent',
                                            'ManagePermissions':'context_agent',
                                            'Unknown':'context_agent',
                                            },
                               'constraints':['Viewer>=Editor']
                               },
                       }
                     
    members_only_defaults = deepcopy(public_defaults)
    members_only_defaults = overlay(members_only_defaults, {'Profile':{'defaults':{'Viewer':'all_members_group'}},
                                                            'User': {'defaults':{'Viewer':'all_members_group'}}})

    inactive_defaults = deepcopy(members_only_defaults)
    inactive_defaults['User']['defaults'] = {'Unknown':'context_admin'} 
    inactive_defaults['Profile']['defaults'] = {'Unknown':'context_admin'} 
    inactive_defaults['Link']['defaults'] = {'Unknown':'context_admin'} 
    inactive_defaults['HostInfo']['defaults'] = {'Unknown':'context_admin'} 

    
    return {'public':public_defaults,
            'members_only':members_only_defaults,
            'inactive':inactive_defaults}
    
AgentDefaults = setup_defaults()
SetAgentDefaults(User, AgentDefaults)
