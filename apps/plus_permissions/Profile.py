
# Permissions for OurPost, an example                                                                                                                        
from django.db import models

from models import Interface, Slider, SliderOption, SecurityTag, PermissionManager
from models import get_permission_system, default_admin_for, InterfaceReadProperty, InterfaceWriteProperty

from apps.profiles.models import Profile

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
        
class ProfileViewer(Interface) : 

    about = InterfaceReadProperty('about')
    location = InterfaceReadProperty('location')
    website = InterfaceReadProperty('website')
    homeplace = InterfaceReadProperty('homeplace')
    organisation = InterfaceReadProperty('organisation')
    role = InterfaceReadProperty('role')

    display_name = InterfaceReadProperty('display_name')
    title = InterfaceReadProperty('title')

    @classmethod
    def get_id(self) : 
        return 'Profile.Viewer'

ProfileEmailAddressViewer = read_interface('email_address','Profile.ProfileEmailAddressViewer')
ProfileHomeViewer = read_interface('home','Profile.EmailAddressViewer')
ProfileWorkViewer = read_interface('work','Profile.WorkViewer')
ProfileMobileViewer = read_interface('mobile','Profile.MobileViewer')
ProfileFaxViewer = read_interface('fax','Profile.FaxViewer')
ProfileAddressViewer = read_interface('address','Profile.AddressViewer')
ProfileSkypeViewer = read_interface('skype_id','SkypeViewer')
ProfileSipViewer = read_interface('sip_id','SipViewer')


class ProfileEditor(Interface) : 
    about = InterfaceWriteProperty('about')
    location = InterfaceWriteProperty('location')
    website = InterfaceWriteProperty('website')

    organisation = InterfaceWriteProperty('organisation')
    role = InterfaceWriteProperty('role')

    display_name = InterfaceWriteProperty('display_name')
    title = InterfaceWriteProperty('title')

    mobile = InterfaceWriteProperty('mobile')
    email_address = InterfaceWriteProperty('email_address')
    address = InterfaceWriteProperty('address')
    skype_id = InterfaceWriteProperty('skype_id')
    sip_id = InterfaceWriteProperty('sip_id')
    website = InterfaceWriteProperty('website')
    homeplace = InterfaceWriteProperty('homeplace')
    
    @classmethod
    def get_id(self) :
        return 'Profile.Editor'


class ProfilePermissionManager(PermissionManager) :
    def register_with_interface_factory(self,interface_factory) :
        self.interface_factory = interface_factory
        interface_factory.add_type(Profile)
        interface_factory.add_interface(Profile,'Viewer',ProfileViewer)
        interface_factory.add_interface(Profile,'Editor',ProfileEditor)
        interface_factory.add_interface(Profile,'EmailAddressViewer',ProfileEmailAddressViewer)
        interface_factory.add_interface(Profile,'WorkViewer',ProfileWorkViewer)

    def make_slider_options(self,resource,owner,creator) :
        options = [
            SliderOption('root',get_permission_system().get_anon_group()),
            SliderOption('all_members',get_permission_system().get_all_members_group()),
            SliderOption(owner.display_name,owner),
            SliderOption(creator.display_name,creator)
        ]
        default_admin = default_admin_for(owner)
        if not default_admin is None :
            options.append( SliderOption(default_admin.display_name,default_admin) )
        return options

    def setup_defaults(self,resource, owner, creator) :
        print "AAA %s, %s, %s" % (resource,owner,creator)
        options = self.make_slider_options(resource,owner,creator)
        interfaces = self.get_interfaces()
        print "BBB"
        print options
        print interfaces 

        slide = interfaces['Viewer'].make_slider_for(resource,options,owner,0)
        slide = interfaces['Editor'].make_slider_for(resource,options,owner,2)
        slide = interfaces['EmailAddressViewer'].make_slider_for(resource,options,owner,1)
        slide = interfaces['WorkViewer'].make_slider_for(resource,options,owner,0)

        #ipdb.set_trace()


        
get_permission_system().add_permission_manager(Profile,ProfilePermissionManager(Profile))

# ========= Signal handlers


def setup_default_permissions(sender,**kwargs):
    # This signalled by Profile.save()
    # tests if there are already permissions for the profile and if not, creates defaults
    profile = kwargs['instance']
    signal = kwargs['signal']
    
    ps = get_permission_system()

    try :
        ps.get_permission_manager(Profile)
    except :
        ps.add_permission_manager(Profile,ProfilePermissionManager(Profile))
        
    if not get_permission_system().has_permissions(profile) :
        ps.get_permission_manager(Profile).setup_defaults(profile,profile.user,profile.user)

post_save.connect(setup_default_permissions,sender=Profile)

