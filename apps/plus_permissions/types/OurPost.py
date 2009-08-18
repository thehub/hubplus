
# Permissions for OurPost, an example 
from django.db import models
from apps.plus_permissions.models import SetSliderOptions, SetAgentSecurityContext, SetAgentDefaults, SetPossibleTypes
from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.hubspace_compatibility.models import TgGroup

from apps.plus_permissions.OurPost import *


# This represents a typical model type from another django or pinax app
content_type = OurPost

# And these are the "child" types that can be created inside this type. 
# Currently OurPost has none, but, for example, a TgGroup can have OurPosts or WikiPages etc.
child_types = []


# Here's the wrapping we have to put around it.

class OurPostViewer: 
    title = InterfaceReadProperty
    body = InterfaceReadProperty

class OurPostEditor: 
    title = InterfaceWriteProperty
    body = InterfaceWriteProperty
    delete = InterfaceCallProperty

class OurPostCommentor:
    pass


from apps.plus_permissions.interfaces import add_type_to_interface_map, get_interface_map

OurPostInterfaces = {'Viewer':OurPostViewer,
                     'Editor':OurPostEditor,
                     'Commentor':OurPostCommentor}

add_type_to_interface_map(OurPost, OurPostInterfaces)


SliderOptions = {'InterfaceOrder':['Viewer', 'Editor','Commentor']}
SetSliderOptions(TgGroup, SliderOptions)




