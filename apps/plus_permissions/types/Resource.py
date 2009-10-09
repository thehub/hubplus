from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, InterfaceReadWriteProperty
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents, SetSliderOptions, SliderOptions, SetTypeLabels
from apps.plus_resources.models import Resource

content_type = Resource

class ResourceViewer :
    title = InterfaceReadProperty
    description = InterfaceReadProperty
    download_url = InterfaceCallProperty
    author = InterfaceReadProperty

    license = InterfaceReadProperty
    resource = InterfaceReadProperty
    created_by = InterfaceReadProperty

    stub = InterfaceReadProperty
    name = InterfaceReadProperty

    in_agent = InterfaceReadProperty

class ResourceManager :
    delete = InterfaceCallProperty

from apps.plus_permissions.models import add_type_to_interface_map
ResourceInterfaces = {'Viewer': ResourceViewer,  'Manager' : ResourceManager  }
add_type_to_interface_map(Resource, ResourceInterfaces)

if not SliderOptions.get(Resource, False):
    SetSliderOptions(Resource, {'InterfaceOrder':['Viewer', 'Manager'], 'InterfaceLabels':{}})

child_types = []
SetPossibleTypes(Resource, child_types)
SetTypeLabels(content_type, 'Upload')

