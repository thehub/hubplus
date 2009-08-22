from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents
from apps.hubspace_compatibility.models import TgGroup
from apps.plus_contacts.models import Application, Contact
from apps.plus_permissions.site import Site
from django.db.models.signals import post_save
import datetime

content_type = Site

# we need a special set_permissions interface which is only editable by the scontext_admin and determines who can set permissions or override them for an object. 

class SiteManager: 
    pk = InterfaceReadProperty
    create_group = InterfaceCallProperty


from apps.plus_permissions.models import add_type_to_interface_map

SiteInterfaces = {
    'Manager': SiteManager 
    }

add_type_to_interface_map(Site, SiteInterfaces)


# use InterfaceOrder to draw the slider and constraints, these are used in rendering the sliders and in validating the results
# these exist on a per type basis and are globals for their type.
# they don't need to be stored in the db
SliderOptions = {'InterfaceOrder':['Manager']}
SetSliderOptions(Site, SliderOptions) 


# ChildTypes are used to determine what types of objects can be created in this security context (and acquire security context from this). These are used when creating an explicit security context for an object of this type. 

child_types = [TgGroup, Application, Contact]
SetPossibleTypes(Site, child_types)


# if the security context is in this agent, this set of slider_agents apply, irrespective of the type of resource they are
def get_slider_agents(scontext)  : 
    return [
            ('anonymous_group', get_anonymous_group().get_ref()),
            ('all_members_group', get_all_members_group().get_ref()),
            ('context_agent', get_all_members_group().get_ref()), 
            ('creator', get_creator_agent()),
            ('context_admin', get_all_members_group().get_admin_group().get_ref())
           ]

SetSliderAgents(Site, get_slider_agents)


# The agent must have a set of default levels for every type which can be created within it. Other objects don't need these as they will be copied from acquired security context according to the possible types available at the "lower" level. We have different AgentDefaults for different group types e.g. standard, public, or private.

#constraints - note that "higher" means wider access. Therefore if "anonymous can't edit" we must set that Editor<$anonymous OR if Editor functionality can't be given to a wider group than Viewer then we must set Editor < Viewer.
AgentDefaults = {'standard':
                     {'Site' : 
                          {'defaults':
                               {'Manager':'context_admin'},
                           'constraints':
                               [] 
                           },
                      'TgGroup':
                          {'defaults':
                               {'Viewer':'anonymous_group', 
                                'Editor':'creator',
                                'Invite':'context_agent',
                                'ManageMembers':'creator',
                                'Join':'all_members_group',
                                'Unknown': 'context_agent'
                                },                           
                           'constraints':
                               ['Viewer>=Editor', 'Invite>=ManageMembers', 'Join>=ManageMembers', 'ManageMembers<=$anonymous']
                           },
                      
                      'Application':
                          { 'defaults' : {'Viewer':'all_members_group',
                                          'Editor':'creator',
                                          'Accept':'context_agent',
                                          },
                            'constraints':['Viewer>=Editor', 'Editor<$anonymous_group']
                            },
                      
                      'Contact':
                          { 'defaults' : {'ContactAdmin':'creator',
                                          },
                            'constraints':[]
                            }
                      },

                 }

SetAgentDefaults(Site, AgentDefaults)


