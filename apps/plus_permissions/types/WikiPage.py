
# Permissions for OurPost, an example 
from django.db import models

from apps.plus_permissions.models import SetSliderOptions, SetAgentSecurityContext, SetAgentDefaults, SetPossibleTypes, SetSliderAgents, SliderOptions, add_type_to_interface_map, get_interface_map

from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.plus_groups.models import TgGroup

from apps.plus_wiki.models import WikiPage
content_type = WikiPage

from apps.plus_permissions.default_agents import get_or_create_root_location, get_anonymous_group, get_all_members_group, get_creator_agent


# This represents a typical model type from another django or pinax app


# And these are the "child" types that can be created inside this type. 
# Currently OurPost has none, but, for example, a TgGroup can have OurPosts or WikiPages etc.
child_types = []
SetPossibleTypes(content_type, child_types)

# Here's the wrapping we have to put around it.

class WikiPageViewer: 
    name = InterfaceReadProperty
    title = InterfaceReadProperty
    content = InterfaceReadProperty
    licence = InterfaceReadProperty
    links_to = InterfaceReadProperty

class WikiPageEditor: 
    title = InterfaceWriteProperty 
    content = InterfaceWriteProperty
    licence = InterfaceWriteProperty

class WikiPageDelete:
    delete = InterfaceCallProperty


if not get_interface_map(WikiPage):
    WikiPageInterfaces = {'Viewer':WikiPageViewer,
                          'Editor':WikiPageEditor,
                          'Delete':WikiPageDelete}

    add_type_to_interface_map(content_type, WikiPageInterfaces)

if not SliderOptions.get(WikiPage, False):
    SetSliderOptions(WikiPage, {'InterfaceOrder':['Viewer', 'Editor','Commentor']})



