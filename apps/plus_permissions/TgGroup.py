
from django.db import models

from models import Interface, Slider, SliderOption, SecurityTag, PermissionManager
from models import get_permission_system, default_admin_for, InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty

from apps.hubspace_compatibility.models import TgGroup

from django.db.models.signals import post_save

import ipdb

# Here's the wrapping we have to put around it. 

def read_interface(name,id) :
    class ReadInterface(Interface) : 
        @classmethod
        def get_id(self):
            return id
    setattr(ReadInterface, name, InterfaceReadProperty(name))
    return ReadInterface
        
class TgGroupViewer(Interface) : 

    pk = InterfaceReadProperty('pk')
    about = InterfaceReadProperty('about')
    location = InterfaceReadProperty('location')
    website = InterfaceReadProperty('website')
    display_name = InterfaceReadProperty('display_name')
    groupextras = InterfaceReadProperty('groupextras')

    apply = InterfaceCallProperty('join')
    leave = InterfaceCallProperty('leave')

    @classmethod
    def get_id(self) : 
        return 'TgGroup.Viewer'

#example from Profile
#ProfileEmailAddressViewer = read_interface('email_address','Profile.EmailAddressViewer')


class TgGroupEditor(Interface) : 
    pk = InterfaceReadProperty('pk')
    about = InterfaceWriteProperty('about')
    location = InterfaceWriteProperty('location')
    website = InterfaceWriteProperty('website')

    display_name = InterfaceWriteProperty('display_name')
    
    @classmethod
    def get_id(self) :
        return 'TgGroup.Editor'


class TgGroupJoin(Interface):
    pk = InterfaceReadProperty('pk')
    join = InterfaceCallProperty('join')

    @classmethod
    def get_id(self) :
        return 'TgGroup.Join'   


class TgGroupInviteMember(Interface):
    pk = InterfaceReadProperty('pk')
    invite_member = InterfaceCallProperty('invite_member')

    @classmethod
    def get_id(self) :
        return 'TgGroup.Invite'


class TgGroupManageMembers(Interface):
    pk = InterfaceReadProperty('pk')
    add_member = InterfaceCallProperty('add_member')
    accept_member = InterfaceCallProperty('accept_member')
    remove_member = InterfaceCallProperty('remove_member')

    @classmethod
    def get_id(self) :
        return 'TgGroup.ManageMembers'



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
            SliderOption('All Site Members',get_permission_system().get_all_members_group()),
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

post_save.connect(setup_default_permissions,sender=TgGroup)

