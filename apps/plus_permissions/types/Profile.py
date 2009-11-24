
# Permissions for OurPost, an example                                                                                                                        
from django.db.models.manager import *

from apps.plus_permissions.models import SecurityTag
from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty

from apps.profiles.models import Profile
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents
from apps.plus_links.models import Link

# Here's the wrapping we have to put around it.                                                                                                              

content_type = Profile
child_types = [Link]
SetPossibleTypes(Profile, child_types)

class ProfileViewer: 
    user = InterfaceReadProperty
    about = InterfaceReadProperty
    place = InterfaceReadProperty
    website = InterfaceReadProperty
    homeplace = InterfaceReadProperty
    organisation = InterfaceReadProperty
    role = InterfaceReadProperty

    display_name = InterfaceReadProperty
    title = InterfaceReadProperty
    get_display_name = InterfaceCallProperty

    cc_messages_to_email = InterfaceReadProperty

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
    place = InterfaceWriteProperty
    website = InterfaceWriteProperty

    organisation = InterfaceWriteProperty
    role = InterfaceWriteProperty

    display_name = InterfaceWriteProperty
    title = InterfaceWriteProperty

    mobile = InterfaceWriteProperty
    work = InterfaceWriteProperty
    home = InterfaceWriteProperty
    fax = InterfaceWriteProperty
    email_address = InterfaceWriteProperty
    address = InterfaceWriteProperty
    skype_id = InterfaceWriteProperty
    sip_id = InterfaceWriteProperty
    homeplace = InterfaceWriteProperty

    cc_messages_to_email = InterfaceWriteProperty



from apps.plus_permissions.models import add_type_to_interface_map

ProfileInterfaces = {'Viewer': ProfileViewer,
                     'Editor': ProfileEditor,
                     'EmailAddressViewer' : ProfileEmailAddressViewer,
                     'HomeViewer' : ProfileHomeViewer,
                     'WorkViewer' : ProfileWorkViewer,
                     'MobileViewer' : ProfileMobileViewer,
                     'FaxViewer' : ProfileFaxViewer,
                     'AddressViewer' : ProfileAddressViewer,
                     'SkypeViewer' : ProfileSkypeViewer,
                     'SipViewer' : ProfileSipViewer}


add_type_to_interface_map(Profile, ProfileInterfaces)

SliderOptions = {'InterfaceOrder':['Viewer'], 'InterfaceLabels':{'Viewer':'View', 'Editor':'Edit'}}
SetSliderOptions(Profile, SliderOptions) 


"""
Data for User.py
        slide = interfaces['Viewer'].make_slider_for(resource,options,owner,0,creator)
        slide = interfaces['Editor'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['EmailAddressViewer'].make_slider_for(resource,options,owner,1,creator)
        slide = interfaces['HomeViewer'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['WorkViewer'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['MobileViewer'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['FaxViewer'].make_slider_for(resource,options,owner,2,creator)

        slide = interfaces['AddressViewer'].make_slider_for(resource,options,owner,2,creator)
        slide = interfaces['SkypeViewer'].make_slider_for(resource,options,owner,1,creator)

            SliderOption('World',get_permission_system().get_anon_group()),
            SliderOption('All Members',get_permission_system().get_site_members()),
            SliderOption('Me',owner),
            SliderOption('Hosts',creator)
"""



