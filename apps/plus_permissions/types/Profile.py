
# Permissions for OurPost, an example                                                                                                                        
from django.db.models.manager import *

from apps.plus_permissions.models import SecurityTag
from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty

from apps.profiles.models import Profile

from apps.hubspace_compatibility.models import TgGroup

import ipdb

# Here's the wrapping we have to put around it.                                                                                                              

content_type = Profile
        
class ProfileViewer: 
    about = InterfaceReadProperty
    location = InterfaceReadProperty
    website = InterfaceReadProperty
    homeplace = InterfaceReadProperty
    organisation = InterfaceReadProperty
    role = InterfaceReadProperty

    display_name = InterfaceReadProperty
    title = InterfaceReadProperty

    @classmethod
    def get_id(self) : 
        return 'Profile.Viewer'

class ProfileEmailAddressViewer:
    email_address = InterfaceReadProperty

class ProfileHomeViewer:
    home = InterfaceReadProperty

class ProfileWorkViewer:
    work = InterfaceReadProperty

class ProfileMobileViewer:
    mobile = InterfaceReadProperty

class ProfileFaxViewer:
    fax = InterfaceReadProperty

class ProfileAddressViewer:
    address = InterfaceReadProperty

class ProfileSkypeViewer:
    skype_id = InterfaceReadProperty

class ProfileSipViewer:
    sip_id = InterfaceReadProperty

class ProfileEditor: 
    pk = InterfaceReadProperty
    about = InterfaceWriteProperty
    location = InterfaceWriteProperty
    website = InterfaceWriteProperty

    organisation = InterfaceWriteProperty
    role = InterfaceWriteProperty

    display_name = InterfaceWriteProperty
    title = InterfaceWriteProperty

    mobile = InterfaceWriteProperty
    email_address = InterfaceWriteProperty
    address = InterfaceWriteProperty
    skype_id = InterfaceWriteProperty
    sip_id = InterfaceWriteProperty
    website = InterfaceWriteProperty
    homeplace = InterfaceWriteProperty

def display_name(x) :
    if x.display_name : return x.display_name 
    if x.username : return x.username
    if x.name : return x.name
    return '%s'%x

"""
class ProfilePermissionManager(PermissionManager) :
    def register_with_interface_factory(self,interface_factory) :
        self.interface_factory = interface_factory
        interface_factory.add_type(Profile)
        interface_factory.add_interface(Profile,'Viewer',ProfileViewer)
        interface_factory.add_interface(Profile,'Editor',ProfileEditor)
        interface_factory.add_interface(Profile,'EmailAddressViewer',ProfileEmailAddressViewer)
        interface_factory.add_interface(Profile,'HomeViewer',ProfileHomeViewer)
        interface_factory.add_interface(Profile,'WorkViewer',ProfileWorkViewer)
        interface_factory.add_interface(Profile,'MobileViewer',ProfileMobileViewer)
        interface_factory.add_interface(Profile,'FaxViewer',ProfileFaxViewer)

        interface_factory.add_interface(Profile,'AddressViewer',ProfileAddressViewer)
        interface_factory.add_interface(Profile,'SkypeViewer',ProfileSkypeViewer)
        interface_factory.add_interface(Profile,'SipViewer',ProfileSipViewer)


    def setup_defaults(self,resource, owner, creator) :
        options = self.make_slider_options(resource,owner,creator)
        self.save_defaults(resource,owner,creator)

        interfaces = self.get_interfaces()

        slide = interfaces['Viewer'].make_slider_for(resource,options,owner,0,creator)
        slide = interfaces['Editor'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['EmailAddressViewer'].make_slider_for(resource,options,owner,1,creator)
        slide = interfaces['HomeViewer'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['WorkViewer'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['MobileViewer'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['FaxViewer'].make_slider_for(resource,options,owner,2,creator)

        slide = interfaces['AddressViewer'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['SkypeViewer'].make_slider_for(resource,options,owner,1,creator)


    def main_json_slider_group(self,resource) :
        json = self.json_slider_group('Profile Permissions', 'Use these sliders to set overall permissions on your profile', resource, ['Viewer','Editor'], [0,0], [[0,1]])
        return json

    def make_slider_options(self,resource,owner,creator) :
        options = [
            SliderOption('World',get_permission_system().get_anon_group()),
            SliderOption('All Members',get_permission_system().get_site_members()),
            SliderOption('Me',owner),
            SliderOption('Hosts',creator)

        ]

        default_admin = default_admin_for(owner)

        if not default_admin is None :
            options.append( SliderOption(default_admin.display_name,default_admin) )

        return options
        
        #ipdb.set_trace()
"""
