from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, InterfaceReadWriteProperty
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents, SetSliderOptions, SliderOptions, SetTypeLabels, SetVisibleTypes
from apps.plus_resources.models import Resource

content_type = Resource

class ResourceViewer :
    title = InterfaceReadProperty
    description = InterfaceReadProperty
    download_url = InterfaceCallProperty
    get_file_name = InterfaceCallProperty
    author = InterfaceReadProperty

    license = InterfaceReadProperty
    resource = InterfaceReadProperty
    created_by = InterfaceReadProperty
    
    stub = InterfaceReadProperty
    name = InterfaceReadProperty
    get_display_name = InterfaceReadProperty
    in_agent = InterfaceReadProperty

class ResourceEditor :
    set_name = InterfaceCallProperty
    title = InterfaceWriteProperty
    description = InterfaceWriteProperty
    author = InterfaceWriteProperty
    license = InterfaceWriteProperty
    resource = InterfaceWriteProperty
    stub = InterfaceWriteProperty
    name= InterfaceWriteProperty
    in_agent = InterfaceWriteProperty
    
    
class ResourceManager :
    delete = InterfaceCallProperty
    move_to_new_group = InterfaceCallProperty

class ResourceCommentor:
    comment = InterfaceCallProperty

class ResourceDelete :
    delete = InterfaceCallProperty

from apps.plus_permissions.models import add_type_to_interface_map
ResourceInterfaces = {
    'Viewer': ResourceViewer,
    'Editor': ResourceEditor,
    'Commentor' : ResourceCommentor,
    'Delete' : ResourceDelete, 
    'Manager' : ResourceManager,
  }
add_type_to_interface_map(Resource, ResourceInterfaces)

if not SliderOptions.get(Resource, False):
    SetSliderOptions(Resource, {'InterfaceOrder':['Viewer', 'Editor', 'Commentor', 'Manager'], 'InterfaceLabels':{'Viewer':'View', 'Editor':'Edit', 'Commentor':'Comment', 'ManagePermissions':'Change Permissions'}})

child_types = []
SetPossibleTypes(Resource, child_types)
SetTypeLabels(content_type, 'Upload')
SetVisibleTypes(content_type,[Resource])
