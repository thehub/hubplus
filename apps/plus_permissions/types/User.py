from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, secure_wrap
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents
from apps.plus_permissions.default_agents import get_all_members_group, get_anonymous_group, get_creator_agent

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from apps.profiles.models import Profile

import datetime


# We need our own get_or_create

from apps.plus_groups.models import User

def create_user(user_name, email_address, password='dummy') :
    """create a User
    """


    if User.objects.filter(username=user_name).count() < 0 :
        user = User.objects.get(username=user_name)
    else :

        user = User(username=user_name, password=password, email=email_address)
        user.email_address=email_address
        user.user_name = user_name
        user.save()
        
        setup_user_security(user)

        user.create_Profile(user,user=user)

    return user


def setup_user_security(user):
    user.to_security_context()
    sec_context = user.get_security_context()
                    
    sec_context.set_context_agent(user.get_ref())
    sec_context.set_context_admin(get_all_members_group().get_admin_group().get_ref())
    sec_context.save()
        
    sec_context.set_up()

    ref = user.get_ref()
    ref.creator = user
    ref.save()


content_type = User

# we need a special set_permissions interface which is only editable by the scontext_admin and determines who can set permissions or override them for an object. 


from apps.plus_permissions.models import add_type_to_interface_map

class UserViewer:
    pk = InterfaceReadProperty
    username = InterfaceReadProperty
    get_profile = InterfaceCallProperty

UserInterfaces = {
    'Viewer':UserViewer
    }

add_type_to_interface_map(User, UserInterfaces)


# use InterfaceOrder to draw the slider and constraints, these are used in rendering the sliders and in validating the results
# these exist on a per type basis and are globals for their type.
# they don't need to be stored in the db
SliderOptions = {'InterfaceOrder':[]}
SetSliderOptions(User, SliderOptions) 


# if the security context is in this agent, this set of slider_agents apply, irrespective of the type of resource they are
def get_slider_agents(scontext)  : 
    return [
            ('anonymous_group', get_anonymous_group().get_ref()),
            ('all_members_group', get_all_members_group().get_ref()), 
            ('context_agent', scontext.context_agent), 
            ('creator', get_creator_agent()),
            ('context_admin', scontext.context_admin)
           ]

SetSliderAgents(User, get_slider_agents)


# ChildTypes are used to determine what types of objects can be created in this security context (and acquire security context from this). These are used when creating an explicit security context for an object of this type. 

child_types = [Profile]
SetPossibleTypes(User, child_types)

# The agent must have a set of default levels for every type which can be created within it. Other objects don't need these as they will be copied from acquired security context according to the possible types available at the "lower" level. We have different AgentDefaults for different group types e.g. standard, public, or private.

#constraints - note that "higher" means wider access. Therefore if "anonymous can't edit" we must set that Editor<$anonymous OR if Editor functionality can't be given to a wider group than Viewer then we must set Editor < Viewer.
AgentDefaults = {'public':

                     {'User':
                          {'defaults': {
                                'Viewer': 'all_members_group',
                                'Unknown': 'context_agent'
                                },                           
                           'constraints':
                               []
                           },
                      'Profile':
                          { 'defaults' : {'Viewer':'anonymous_group',
                                          'Editor':'creator',
                                          'Unknown': 'context_agent'},
                            'constraints':[]
                            },
                      },
                 

                 'private':
                     {'User':
                          {'defaults': {
                                'Unknown': 'context_agent'
                                },                           
                           'constraints':
                               []
                           },
                      'Profile':
                          { 'defaults' : {'Viewer':'anonymous_group',
                                          'Editor':'creator',
                                          'Unknown': 'context_agent'},
                            'constraints':[]
                            },
                      },
                 }
                 

SetAgentDefaults(User, AgentDefaults)
