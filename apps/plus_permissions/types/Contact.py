from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, InterfaceReadWriteProperty
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents

from apps.plus_contacts.models import Contact

from apps.plus_groups.models import TgGroup

from django.db.models.signals import post_save
import datetime

content_type = Contact

from apps.plus_permissions.default_agents import get_or_create_root_location, get_anonymous_group, get_all_members_group, get_creator_agent

# we need a special set_permissions interface which is only editable by the scontext_admin and 
# determines who can set permissions or override them for an object. 

class ContactAdmin: 
    pk = InterfaceReadProperty
    first_name = InterfaceReadWriteProperty
    last_name = InterfaceReadWriteProperty
    organisation = InterfaceReadWriteProperty
    email_address = InterfaceReadWriteProperty
    location = InterfaceReadWriteProperty
    apply_msg = InterfaceReadWriteProperty
    find_out = InterfaceReadWriteProperty
    invited_by = InterfaceReadWriteProperty

    become_member = InterfaceCallProperty
    invite = InterfaceCallProperty

class ContactInvite:
    pk = InterfaceReadProperty
    invite = InterfaceCallProperty
    group_invite_message = InterfaceCallProperty

from apps.plus_permissions.models import add_type_to_interface_map

ContactInterfaces = {'ContactAdmin': ContactAdmin,  'ContactInvite' : ContactInvite  }

add_type_to_interface_map(Contact, ContactInterfaces)


# use InterfaceOrder to draw the slider and constraints, these are used in rendering the sliders and in validating the results
# these exist on a per type basis and are globals for their type.
# they don't need to be stored in the db
SliderOptions = {'InterfaceOrder':['ContactAdmin']}
SetSliderOptions(Contact, SliderOptions) 

# ChildTypes are used to determine what types of objects can be created in this security context (and acquire security context from this). These are used when creating an explicit security context for an object of this type. 

child_types = []
SetPossibleTypes(Contact, child_types)


