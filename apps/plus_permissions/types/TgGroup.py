from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty
from apps.plus_permissions.models import SetSliderOptions, SliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents, PossibleTypes, get_interface_map, SetVisibleAgents
from apps.plus_groups.models import TgGroup
from apps.plus_permissions.OurPost import OurPost
from apps.plus_contacts.models import Application, Contact
from apps.plus_wiki.models import WikiPage
from apps.profiles.models import Profile
from apps.plus_permissions.site import Site
from apps.plus_links.models import Link
from apps.plus_resources.models import Resource

from django.db.models.signals import post_save
import datetime
from copy import deepcopy

content_type = TgGroup


from apps.plus_permissions.default_agents import get_or_create_root_location, get_anonymous_group, get_all_members_group, get_creator_agent

def setup_group_security(group, context_agent, context_admin, creator, permission_prototype):
    group.to_security_context()
    sec_context = group.get_security_context() 
    sec_context.set_context_agent(context_agent.get_ref())
    sec_context.set_context_admin(context_admin.get_ref())
    sec_context.save()
    group.add_member(creator)
    group.add_member(context_admin)

    group.save()
    group.get_security_context().set_up(permission_prototype)
    
    ref = group.get_ref()
    ref.creator = creator
    ref.permission_prototype = permission_prototype
    ref.save()

    if group.id != get_all_members_group().id :
        get_all_members_group().add_member(group)



# override object managers, filter, get, get_or_create
def get_or_create(group_name=None, display_name=None, place=None, level=None, user=None, 
                  group_type='interest', description='', permission_prototype='public') :
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
        group = TgGroup(group_name=group_name, display_name=display_name, level=level, 
                        place=place, description=description, group_type=group_type)
        group.save()

        if level == 'member':
            admin_group, created = TgGroup.objects.get_or_create(
                group_name=group_name + "_hosts", 
                display_name=display_name + " Hosts", 
                level='host',
                place=place,
                user=user, 
                description="Admin Group for %s" % display_name, 
                )

            setup_group_security(group, group, admin_group, user, permission_prototype)
        elif level == 'host':
            setup_group_security(group, group, group, user, 'private')

    return group, created

# XXX will be moved to patch.py
#TgGroup.objects.get_or_create = get_or_create

def get_admin_group(self) :
    return self.get_security_context().context_admin.obj 

TgGroup.get_admin_group = get_admin_group
 
# we need a special set_permissions interface which is only editable by the scontext_admin and determines who can set permissions or override them for an object. 

class TgGroupViewer: 
    pk = InterfaceReadProperty
    description = InterfaceReadProperty
    place = InterfaceReadProperty
    website = InterfaceReadProperty
    display_name = InterfaceReadProperty

    group_type = InterfaceReadProperty
    address = InterfaceReadProperty

    apply = InterfaceCallProperty
    leave = InterfaceCallProperty
    get_users = InterfaceCallProperty
    get_no_members = InterfaceCallProperty
    get_admin_group = InterfaceCallProperty
    get_display_name = InterfaceCallProperty # huh
    display_name = InterfaceReadProperty

class TgGroupEditor: 
    pk = InterfaceReadProperty
    description = InterfaceWriteProperty
    place = InterfaceWriteProperty
    website = InterfaceWriteProperty
    display_name = InterfaceWriteProperty    
    message_members = InterfaceCallProperty

class TgGroupJoin:
    pk = InterfaceReadProperty
    join = InterfaceCallProperty
    leave = InterfaceCallProperty

class TgGroupInviteMember:
    pk = InterfaceReadProperty
    invite_member = InterfaceCallProperty

class TgGroupComment:
    pk = InterfaceReadProperty
    comment = InterfaceCallProperty

class TgGroupUploader:
    upload = InterfaceCallProperty

class TgGroupManageMembers:
    pk = InterfaceReadProperty
    add_member = InterfaceCallProperty
    accept_member = InterfaceCallProperty
    remove_member = InterfaceCallProperty

class SetManagePermissions:
    pass


from apps.plus_permissions.models import add_type_to_interface_map

if not get_interface_map(TgGroup):
    TgGroupInterfaces = {'Viewer': TgGroupViewer,
                         'Editor': TgGroupEditor,
                         'Invite': TgGroupInviteMember,
                         'ManageMembers': TgGroupManageMembers,
                         'Join': TgGroupJoin,
                         'Comment':TgGroupComment,
                         'Uploader':TgGroupUploader,
                         'SetManagePermissions':SetManagePermissions}
    add_type_to_interface_map(TgGroup, TgGroupInterfaces)


# use InterfaceOrder to draw the slider and constraints, these are used in rendering the sliders and in validating the results
# these exist on a per type basis and are globals for their type.
# they don't need to be stored in the db
if not SliderOptions.get(TgGroup, False):
    SetSliderOptions(TgGroup, {'InterfaceOrder':['Viewer', 'Editor', 'Invite', 'Join', 'Uploader', 'ManageMembers', 'ManagePermissions'], 
                               'InterfaceLabels':{'Viewer':'View',
                                                  'Editor': 'Edit',
                                                  'ManageMembers': 'Manage Membership',
                                                  'ManagePermissions':'Change Permissions'}})


# ChildTypes are used to determine what types of objects can be created in this security context (and acquire security context from this). These are used when creating an explicit security context for an object of this type. 
if TgGroup not in PossibleTypes:
    child_types = [OurPost, Site, Application, Contact, Profile, WikiPage, Link, Resource]
    SetPossibleTypes(TgGroup, child_types)



# if the security context is in this agent, this set of slider_agents apply, irrespective of the type of resource they are
def get_slider_agents(scontext)  : 
    return [
            ('anonymous_group', get_anonymous_group().get_ref()),
            ('all_members_group', get_all_members_group().get_ref()), 
            ('context_agent', scontext.context_agent), 
            ('creator', get_creator_agent()),
            ('context_admin', scontext.context_admin)
           ]

SetSliderAgents(TgGroup, get_slider_agents)


def visible_agents():
    return ['anonymous_group', 'all_members_group', 'context_agent', 'creator', 'context_admin']
SetVisibleAgents(TgGroup, visible_agents())


# The agent must have a set of default levels for every type which can be created within it. Other objects don't need these as they will be copied from acquired security context according to the possible types available at the "lower" level. We have different AgentDefaults for different group types e.g. standard, public, or private.

#constraints - note that "higher" means wider access. Therefore if "anonymous can't edit" we must set that Editor<$anonymous OR if Editor functionality can't be given to a wider group than Viewer then we must set Editor < Viewer.

public_defaults = {'TgGroup':
                       {'defaults':
                            {'Viewer':'anonymous_group', 
                             'Editor':'creator',
                             'Invite':'context_agent',
                             'ManageMembers':'creator',
                             'Join':'all_members_group',
                             'ManagePermissions':'context_admin',
                             'SetManagePermissions':'context_admin',
                             'Unknown': 'context_agent'
                             },
                        'constraints':
                            ['Viewer>=Editor', 'Invite>=ManageMembers', 'Join>=ManageMembers', 'ManageMembers<=$anonymous_group', 'ManagePermissions<=$context_agent']
                        },
                   'WikiPage':
                       {'defaults':
                            {'Viewer':'anonymous_group',
                             'Editor':'context_agent',
                             'Creator':'creator',
                             'Delete':'context_admin',
                             'Commentor':'context_agent',
                             'Unknown':'context_agent',
                             'ManagePermissions':'creator'},
                        'constraints': ['Viewer>=Editor', 'Editor<$anonymous_group', 'Viewer>=Commentor']
                        },
                   'OurPost':
                       { 'defaults' : 
                         {'Viewer':'all_members_group',
                          'Editor':'creator',
                          'Commentor':'context_agent',
                          'ManagePermissions':'creator',
                          'Unknown': 'context_agent'},
                         'constraints':['Viewer>=Editor', 'Editor<$anonymous_group']
                         },
                   'Site' : 
                   {'defaults':
                        {'create_Application':'anonymous_group',
                         'ManagePermissions':'context_admin',
                         'Unknown': 'context_agent'}, #shouldn't these perms be set to the context_admin?
                    'constraints': [] 
                    },
                   'Application':
                       {'defaults' : 
                        {'Viewer':'all_members_group',
                         'Editor':'creator',
                         'Accept':'all_members_group',
                         'ManagePermissions':'context_admin',
                         'Unknown': 'context_agent'
                         },
                        'constraints':['Viewer>=Editor', 'Editor<$anonymous_group'] 
                        },                      
                   'Contact':
                       {'defaults' : 
                        {'ContactAdmin':'context_admin',
                         'ContactInvite':'all_members_group',
                         'ManagePermissions':'context_admin',
                         'Unknown': 'context_agent'
                         },               
                        'constraints':[]
                        },
                   'Link':
                       {'defaults' : 
                          { 'Viewer': 'anonymous_group',
                            'Manager': 'context_agent',
                            'ManagePermissions':'context_admin',
                            'Unknown': 'context_agent',
                          },
                          'constraints':['Viewer>=Manager']
                        },

                   'Resource':
                       {'defaults' :
                          { 'Viewer': 'anonymous_group',
                            'Manager': 'context_agent',
                            'ManagePermissions':'context_admin',
                            'Unknown': 'context_agent',
                          },
                          'constraints':['Viewer>=Manager']
                        },


                   'Profile':
                       {'defaults': 
                        {'Viewer': 'anonymous_group',
                         'Editor': 'creator',
                         'EmailAddressViewer' : 'context_agent',
                         'HomeViewer' : 'context_agent',
                         'WorkViewer' : 'context_agent',
                         'MobileViewer' : 'context_agent',
                         'FaxViewer' : 'context_agent',
                         'AddressViewer' : 'context_agent',
                         'SkypeViewer' : 'context_agent',
                         'SipViewer' : 'context_agent',
                         'ManagePermissions':'context_admin',
                         'Unknown' : 'creator',
                         },
                        'constraints':[]
                        }
                   }


# start by cloning the public, then we'll over-ride the differences using plus_lib/utils/overlay
private_defaults = deepcopy(public_defaults)
open_defaults = deepcopy(public_defaults)
invite_defaults = deepcopy(public_defaults)

AgentDefaults = {'public':public_defaults,
                 'private':private_defaults,
                 'open' : open_defaults,
                 'invite' : invite_defaults}


#AgentDefaults = {'public':
#                     {'TgGroup':
#                          {'defaults':
#                               {'Viewer':'anonymous_group', 
#                                'Editor':'creator',
#                                'Invite':'context_agent',
#                                'ManageMembers':'creator',
#                                'Join':'all_members_group',
#                                'Unknown': 'context_agent'
#                                },                           
#                           'constraints':
#                               ['Viewer>=Editor', 'Invite>=ManageMembers', 'Join>=ManageMembers', 'ManageMembers<=$anonymous']
#                           },
#                      'WikiPage':
#                          {'defaults':
#                               {'Viewer':'anonymous_group',
#                                'Editor':'context_agent',
#                                'Delete':'context_admin',
#                                'Unknown':'context_agent'},
#                           'constraints': ['Viewer>=Editor', 'Editor<$anonymous_group']
#                           },
#                      'OurPost':
#                          { 'defaults' : {'Viewer':'all_members_group',
#                                          'Editor':'creator',
#                                          'Commentor':'context_agent',
#                                          'Unknown': 'context_agent'},
#                            'constraints':['Viewer>=Editor', 'Editor<$anonymous_group']
#                            },
#                      'Site' : 
#                          {'defaults':
#                                {'create_Application':'anonymous_group',
#                                'Unknown': 'context_agent'},
#                           'constraints':
#                               [] 
#                           },
#                      'Application':
#                          { 'defaults' : {'Viewer':'all_members_group',
#                                          'Editor':'creator',
#                                          'Accept':'all_members_group',
#                                          'Unknown': 'context_agent'
#                                          },
#                            'constraints':['Viewer>=Editor', 'Editor<$anonymous_group']
#                            },                      
#                      'Contact':
#                          { 'defaults' : {'ContactAdmin':'context_admin',
#                                          'ContactInvite':'all_members_group',
#                                          'Unknown': 'context_agent'
#                                          },
#                            'constraints':[]
#                           },
#                      'Profile':
#                          { 'defaults': {'Viewer': 'anonymous_group',
#                                         'Editor': 'creator',
#                                         'EmailAddressViewer' : 'context_agent',
#                                         'HomeViewer' : 'context_agent',
#                                         'WorkViewer' : 'context_agent',
#                                         'MobileViewer' : 'context_agent',
#                                         'FaxViewer' : 'context_agent',
#                                         'AddressViewer' : 'context_agent',
#                                         'SkypeViewer' : 'context_agent',
#                                         'SipViewer' : 'context_agent',
#                                         'Unknown' : 'creator',
#                                         
#                                         },
#                           'constraints':[]
#                           }
#                      },
#                 
#
#                 'private':
#                    {'TgGroup':
#                          {'defaults':
#                               {'Viewer':'context_agent', 
#                                'Editor':'creator',
#                                'Invite':'context_agent',
#                                'ManageMembers':'creator',
#                                'Join':'context_agent',
#                                'Unknown': 'context_admin'
#                               },
#                           'constraints':
#                               ['Viewer>=Editor', 'Invite>=ManageMembers', 'Join>=ManageMembers', 'ManageMembers<=$anonymous']
#                           },
#                      'OurPost': 
#                          {'defaults' : 
#                               {'Viewer':'all_members_group',
#                                'Editor':'creator',
#                                'Commentor':'context_agent',
#                                'Unknown': 'context_agent'},
#                           'constraints':['Viewer>=Editor']
#                           },
#                      'Site' : 
#                          {'defaults':
#                               {'Manager':'context_admin',
#                                'Unknown': 'context_agent'},
#                           'constraints':
#                               [] 
#                           },
#                      'Application':
#                          { 'defaults' : {'Viewer':'all_members_group',
#                                          'Editor':'creator',
#                                          'Accept':'context_agent',
#                                          'Unknown': 'context_agent',
#                                          },
#                            'constraints':['Viewer>=Editor', 'Editor<$anonymous_group']
#                            },                      
#                      'Contact':
#                          { 'defaults' : {'ContactAdmin':'context_admin',
#                                          'ContactInvite':'all_members_group',
#                                          'Unknown': 'context_agent',
#                                          },
#                            'constraints':[]
#                            },
#                      'Profile':
#                          { 'defaults': {'Viewer': 'anonymous_group',
#                                         'Editor': 'creator',
#                                         'EmailAddressViewer' : 'context_agent',
#                                         'HomeViewer' : 'context_agent',
#                                         'WorkViewer' : 'context_agent',
#                                         'MobileViewer' : 'context_agent',
#                                         'FaxViewer' : 'context_agent',
#                                         'AddressViewer' : 'context_agent',
#                                         'SkypeViewer' : 'context_agent',
#                                         'SipViewer' : 'context_agent',
#                                        'Unknown' : 'creator',
#                                        
#                                         },
#                            'constraints':[]
#                            }
#
#
#                      }
#                 }

SetAgentDefaults(TgGroup, AgentDefaults)


