from apps.plus_permissions.models import SecurityTag
from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty


from apps.hubspace_compatibility.models import TgGroup

from django.db.models.signals import post_save

import ipdb

# Here's the wrapping we have to put around it. 

def get_or_create_group(self, group_name, display_name, place) :
    # note : we can't use get_or_create for TgGroup, because the created date clause won't match on a different day                                     
    # from the day the record was created.                                                                                                              
    xs = TgGroup.objects.filter(group_name=group_name)
    if len(xs) > 0 :
        g = xs[0]
    else :
        g = TgGroup(
            group_name=group_name, display_name=display_name, level='member',
            place=place,created=datetime.date.today()
            )
        g.save()
    return g

        
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




context_default_configs = {'TgGroup': { 'target' : "target",
                                        'possible_types' : ['OurPost'],
                                        'slider_agents': ['anonymous_group',
                                                          'all_members_group',
                                                          '$context_agent',
                                                          '$creator',
                                                          '$context_agent_admin'], 
                                        'interfaces':{'Profile':['Profile.Viewer','Profile.Editor','Profile.PhoneViewer','Profile.EmailViewer'],
                                                      'TgGroup':['TgGroup.Viewer','TgGroup.Editor','TgGroup.Join']},
                                        'constraints':{'Profile':[]},
                                        'defaults':{'Profile':{'Viewer':2, 
                                                               'Editor':1}
                                                    }
                                        }
                           }


"""
class TgGroupPermissionManager(PermissionManager) :
    def register_with_interface_factory(self,interface_factory) :
        self.interface_factory = interface_factory
        interface_factory.add_type(TgGroup)
        interface_factory.add_interface(TgGroup,'Viewer',TgGroupViewer)
        interface_factory.add_interface(TgGroup,'Editor',TgGroupEditor)

        interface_factory.add_interface(TgGroup,'Join',TgGroupJoin)
        interface_factory.add_interface(TgGroup,'InviteMember',TgGroupInviteMember)

        interface_factory.add_interface(TgGroup,'ManageMembers',TgGroupManageMembers)


    def make_slider_options(self,resource,owner,creator) :
        options = [
            SliderOption('World',get_permission_system().get_anon_group()),
            SliderOption('All Site Members',get_permission_system().get_site_members()),
            SliderOption(owner.display_name,owner),
        ]

        default_admin = default_admin_for(owner)
        if not default_admin is None :
            options.append( SliderOption(default_admin.display_name,default_admin) )
        return options


    def setup_defaults(self,resource, owner, creator) :
        self.save_defaults(resource,owner,creator)

        options = self.make_slider_options(resource,owner,creator)
        interfaces = self.get_interfaces()

        slide = interfaces['Viewer'].make_slider_for(resource,options,owner,0,creator,creator)
        slide = interfaces['Editor'].make_slider_for(resource,options,owner,3,creator,creator)
        slide = interfaces['Join'].make_slider_for(resource,options,owner,1,creator,creator)
        slide = interfaces['Invite'].make_slider_for(resource,options,owner,2,creator,creator)
        slide = interfaces['ManageMembers'].make_slider_for(resource,options,owner,3,creator,creator)

    def main_json_slider_group(self,resource) :
        json = self.json_slider_group('Group Permissions', 'Use these sliders to set overall permissions on your group', 
               resource, 
               ['Viewer', 'Editor', 'Apply', 'Join', 'ManageMembers'], 
               [0, 3, 1, 2, 3], 
               [[0,1], [0,2], [0,3], [0,4]])
        return json


get_permission_system().add_permission_manager(TgGroup, TgGroupPermissionManager(TgGroup))

# ========= Signal handlers


def setup_default_permissions(sender,**kwargs):
    # This signalled by Profile.save()
    # tests if there are already permissions for the profile and if not, creates defaults
    group = kwargs['instance']
    signal = kwargs['signal']
    
    ps = get_permission_system()
    print "DDD setup_default_permission for TgGroup"
    try :
        ps.get_permission_manager(TgGroup)
    except :
        ps.add_permission_manager(TgGroup, TgGroupPermissionManager(TgGroup))
        
    if not get_permission_system().has_permissions(group) :
        ps.get_permission_manager(TgGroup).setup_defaults(group, group, group)
"""


#post_save.connect(setup_default_permissions, sender=TgGroup)

