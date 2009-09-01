from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, InterfaceReadWriteProperty
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents

from apps.plus_contacts.models import Application

from apps.plus_groups.models import TgGroup

from django.db.models.signals import post_save
import datetime

content_type = Application

from apps.plus_permissions.default_agents import get_or_create_root_location, get_anonymous_group, get_all_members_group, get_creator_agent

# we need a special set_permissions interface which is only editable by the scontext_admin and 
# determines who can set permissions or override them for an object. 

class ApplicationViewer: 
    pk = InterfaceReadProperty
    applicant = InterfaceReadProperty    
    group = InterfaceReadProperty
    request = InterfaceReadProperty
    status = InterfaceReadProperty

    admin_comment = InterfaceReadProperty
    date = InterfaceReadProperty

    is_site_application = InterfaceCallProperty
    requests_group = InterfaceCallProperty

class ApplicationEditor: 
    pk = InterfaceReadProperty
    applicant = InterfaceReadWriteProperty    
    group = InterfaceReadWriteProperty
    request = InterfaceReadWriteProperty
    status = InterfaceReadWriteProperty

    admin_comment = InterfaceReadWriteProperty
    date = InterfaceReadWriteProperty
    accepted_by = InterfaceReadWriteProperty
    
    
class ApplicationAccept:
    pk = InterfaceReadProperty
    accept = InterfaceCallProperty
    generate_accept_url = InterfaceCallProperty
    status = InterfaceReadWriteProperty
    accepted_by = InterfaceReadWriteProperty
    delete = InterfaceCallProperty



from apps.plus_permissions.models import add_type_to_interface_map

ApplicationInterfaces = {'Viewer': ApplicationViewer,
                         'Editor': ApplicationEditor,
                         'Accept': ApplicationAccept
                         }



add_type_to_interface_map(Application, ApplicationInterfaces)


# use InterfaceOrder to draw the slider and constraints, these are used in rendering the sliders and in validating the results
# these exist on a per type basis and are globals for their type.
# they don't need to be stored in the db
SliderOptions = {'InterfaceOrder':['Viewer', 'Editor', 'Accept']}
SetSliderOptions(Application, SliderOptions) 


# ChildTypes are used to determine what types of objects can be created in this security context (and acquire security context from this). These are used when creating an explicit security context for an object of this type. 

child_types = []
SetPossibleTypes(Application, child_types)


