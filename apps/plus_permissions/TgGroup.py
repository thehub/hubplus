
from django.db import models

from models import Interface, Slider, SliderOption, SecurityTag, PermissionManager
from models import get_permission_system, default_admin_for, InterfaceReadProperty, InterfaceWriteProperty

from apps.hubspace_compatibility.models import TgGroup

from django.db.models.signals import post_save

import ipdb

# Here's the wrapping we have to put around it. 

def read_interface(name,id) :
    class ReadInterface(Interface) : 
        @classmethod
        def get_id(self):
            return id
    setattr(ReadInterface,name,InterfaceReadProperty(name))
    return ReadInterface
        
class TgGroupViewer(Interface) : 

    pk = InterfaceReadProperty('pk')
    about = InterfaceReadProperty('about')
    location = InterfaceReadProperty('location')
    website = InterfaceReadProperty('website')
    display_name = InterfaceReadProperty('display_name')
    groupextras = InterfaceReadProperty('groupextras')

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


class TgGroupPermissionManager(PermissionManager) :
    def register_with_interface_factory(self,interface_factory) :
        self.interface_factory = interface_factory
        interface_factory.add_type(TgGroup)
        interface_factory.add_interface(TgGroup,'Viewer',TgGroupViewer)
        interface_factory.add_interface(TgGroup,'Editor',TgGroupEditor)

    def setup_defaults(self,resource, owner, creator) :
        self.save_defaults(resource,owner,creator)

        options = self.make_slider_options(resource,owner,creator)
        interfaces = self.get_interfaces()


        slide = interfaces['Viewer'].make_slider_for(resource,options,owner,0,creator,creator)
        slide = interfaces['Editor'].make_slider_for(resource,options,owner,2,creator,creator)

        #ipdb.set_trace()

get_permission_system().add_permission_manager(TgGroup,TgGroupPermissionManager(TgGroup))

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
        ps.add_permission_manager(TgGroup,TgGroupPermissionManager(TgGroup))
        
    if not get_permission_system().has_permissions(group) :
        ps.get_permission_manager(TgGroup).setup_defaults(group,group,group)

post_save.connect(setup_default_permissions,sender=TgGroup)

