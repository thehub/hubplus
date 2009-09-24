from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, InterfaceReadWriteProperty
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents
from apps.plus_resources.models import Resource

content_type = Resource

class ResourceViewer :
    title = InterfaceReadProperty
    description = InterfaceReadProperty
    download_url = InterfaceCallProperty

class ResourceManager :
    delete = InterfaceCallProperty

from apps.plus_permissions.models import add_type_to_interface_map
ResourceInterfaces = {'Viewer': ResourceViewer,  'Manager' : ResourceManager  }
add_type_to_interface_map(Resource, ResourceInterfaces)


SliderOptions = {'InterfaceOrder':['Viewer', 'Manager']}
SetSliderOptions(Resource, SliderOptions)

child_types = []
SetPossibleTypes(Resource, child_types)

