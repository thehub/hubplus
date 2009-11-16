
# Permissions for OurPost, an example 
from django.db import models

from apps.plus_permissions.models import SetSliderOptions, SetAgentSecurityContext, SetAgentDefaults, SetPossibleTypes, SetSliderAgents, SliderOptions, add_type_to_interface_map, get_interface_map, SetVisibleTypes, SetTypeLabels

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
SetVisibleTypes(content_type, [WikiPage])
SetTypeLabels(content_type, 'Page')


# Here's the wrapping we have to put around it.

class WikiPageViewer: 
    name = InterfaceReadProperty
    title = InterfaceReadProperty
    content = InterfaceReadProperty
    license = InterfaceReadProperty
    links_to = InterfaceReadProperty
    in_agent = InterfaceReadProperty
    stub = InterfaceReadProperty
    created_by = InterfaceReadProperty
    creation_time = InterfaceReadProperty

class WikiPageEditor:
    name_from_title = InterfaceCallProperty
    title = InterfaceWriteProperty
    content = InterfaceWriteProperty
    license = InterfaceWriteProperty
    stub = InterfaceWriteProperty

class WikiPageCreator:
    created_by = InterfaceWriteProperty

class WikiPageDelete:
    delete = InterfaceCallProperty

class WikiPageCommentor: 
    comment = InterfaceCallProperty


class WikiPageCommentViewer:
    view_comments = InterfaceReadProperty

if not get_interface_map(WikiPage):
    WikiPageInterfaces = {'Viewer':WikiPageViewer,
                          'Editor':WikiPageEditor,
                          'Delete':WikiPageDelete,
                          'Creator':WikiPageCreator,
                          "Commentor":WikiPageCommentor,
                          "ViewComments":WikiPageCommentViewer}

    add_type_to_interface_map(content_type, WikiPageInterfaces)

if not SliderOptions.get(WikiPage, False):
    SetSliderOptions(WikiPage, {'InterfaceOrder':['Viewer', 'Editor','Commentor', 'ManagePermissions'], 'InterfaceLabels':{'Viewer':'View', 'Editor':'Edit', 'Commentor':'Comment', 'ManagePermissions':'Change Permissions'}})



