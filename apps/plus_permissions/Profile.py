
# Permissions for OurPost, an example                                                                                                                        
from django.db import models

from models import Interface, Slider, SliderOption, SecurityTag, PermissionManager
from models import get_permission_system, default_admin_for, InterfaceReadProperty, InterfaceWriteProperty

from apps.profiles.models import Profile

from apps.hubspace_compatibility.models import TgGroup

from django.db.models.signals import post_save


# Here's the wrapping we have to put around it.                                                                                                              

class ProfileViewer(Interface) : 

    about = InterfaceReadProperty('about')
    location = InterfaceReadProperty('location')
    website = InterfaceReadProperty('website')

    organisation = InterfaceReadProperty('organisation')
    role = InterfaceReadProperty('role')

    display_name = InterfaceReadProperty('display_name')
    title = InterfaceReadProperty('title')

    website = InterfaceReadProperty('website')
    homeplace = InterfaceReadProperty('homeplace')


class ProfileEditor(Interface) : 
    about = InterfaceWriteProperty('about')
    location = InterfaceWriteProperty('location')
    website = InterfaceWriteProperty('website')

    organisation = InterfaceWriteProperty('organisation')
    role = InterfaceWriteProperty('role')

    display_name = InterfaceWriteProperty('display_name')
    title = InterfaceWriteProperty('title')

    website = InterfaceWriteProperty('website')
    homeplace = InterfaceWriteProperty('homeplace')

    mobile = InterfaceWriteProperty('mobile')
    work = InterfaceWriteProperty('work')
    email2 = InterfaceWriteProperty('email2')
    fax = InterfaceWriteProperty('fax')
    home = InterfaceWriteProperty('home')

    address = InterfaceReadProperty('address')
    skype_id = InterfaceReadProperty('skype_id')
    sip_id = InterfaceReadProperty('sip_id')



class ProfileContactViewer(Interface) :
    mobile = InterfaceReadProperty('mobile')
    work = InterfaceReadProperty('work')
    email2 = InterfaceReadProperty('email2')
    fax = InterfaceReadProperty('fax')
    home = InterfaceReadProperty('home')

    address = InterfaceReadProperty('address')
    skype_id = InterfaceReadProperty('skype_id')
    sip_id = InterfaceReadProperty('sip_id')


class ProfilePermissionManager(PermissionManager) :

    def register_with_interface_factory(self,interface_factory) :
        self.interface_factory = interface_factory
        interface_factory.add_type(Profile)
        interface_factory.add_interface(Profile,'Viewer',ProfileViewer)
        interface_factory.add_interface(Profile,'Editor',ProfileEditor)
        interface_factory.add_interface(Profile,'ContactViewer',ProfileContactViewer)

    def make_slider_options(self,resource,interface_name,owner,creator) :
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

    def make_viewer_slider(self,resource,interface_name,owner,creator) :
        options = self.make_slider_options(resource,interface_name,owner,creator)
        s = Slider(
            tag_name='ProfilePermissionManager.Viewer slider',
            resource=resource,
            interface_id='Profile.Viewer',
            default_agent=self.get_permission_system().get_anon_group(),
            options=options
        )
        s.set_current_option(0)
        return s

    def make_editor_slider(self,resource,interface_name,owner,creator) :
        options = self.make_slider_options(resource,interface_name,owner,creator)
        s = Slider(
            tag_name='ProfilePermissionManager.Editor slider',
            resource=resource,
            interface_id='Profile.Editor',
            default_agent=self.get_permission_system().get_anon_group(),
            options=options
        )
        s.set_current_option(3)
        return s

    def make_contact_viewer_slider(self,resource,interface_name,owner,creator) :
        options = self.make_slider_options(resource,interface_name,owner,creator)
        s = Slider(
            tag_name='ProfilePermissionManager.ContactViewer slider',
            resource=resource,
            interface_id='Profile.ContactViewer',
            default_agent=self.get_permission_system().get_anon_group(),
            options=options
        )
        s.set_current_option(2)
        return s

    def make_slider(self,resource,interface_name,owner,creator) :
        if interface_name == 'Viewer' :
            return self.make_viewer_slider(resource,interface_name,owner,creator)
        elif interface_name == 'Editor' :
            return self.make_editor_slider(resource,interface_name,owner,creator)
        elif interface_name == 'ContactViewer' :
            return self.make_contact_viewer_slider(resource,interface_name,owner,creator)
        else :
            raise NoSliderException(Profile,interface_name)

    def setup_defaults(self,resource, owner, creator) :
        s = self.make_slider(resource,'Viewer',owner,creator)
        s.set_current_option(s.current_idx)
        s = self.make_slider(resource,'Editor',owner,creator)
        s.set_current_option(s.current_idx)
        s = self.make_slider(resource,'ContactViewer',owner,creator)
        s.set_current_option(s.current_idx)


_PROFILE_PERMISSION_MANAGER = None 
def make_permission_manager() : 
    global _PROFILE_PERMISSION_MANAGER
    if not _PROFILE_PERMISSION_MANAGER :
        _PROFILE_PERMISSION_MANAGER=ProfilePermissionManager()
        _PROFILE_PERMISSION_MANAGER.register_with_interface_factory(get_permission_system().get_interface_factory())
    return _PROFILE_PERMISSION_MANAGER

# ========= Signal handlers

def setup_default_permissions(sender,**kwargs):
    # This signalled by Profile.save()
    # tests if there are already permissions for the profile and if not, creates defaults
    profile = kwargs['instance']
    signal = kwargs['signal']
    ps = get_permission_system()
    if not ps.has_permissions(profile) :
        make_permission_manager().setup_defaults(profile,profile.user,profile.user)

post_save.connect(setup_default_permissions,sender=Profile)



