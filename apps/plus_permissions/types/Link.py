from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, InterfaceReadWriteProperty
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents
from apps.plus_links.models import Link

content_type = Link

class LinkViewer :
    text = InterfaceReadProperty
    url = InterfaceReadProperty
    target = InterfaceReadProperty
    service = InterfaceReadProperty

class LinkRemover :
    remove_link = InterfaceCallProperty

class LinkManager :
    delete = InterfaceCallProperty

from apps.plus_permissions.models import add_type_to_interface_map
LinkInterfaces = {'Viewer' : LinkViewer, 'Remover' : LinkRemover, 'Manager' : LinkManager  }
add_type_to_interface_map(Link, LinkInterfaces)


SliderOptions = {'InterfaceOrder':['Viewer', 'Remover', 'Manager']}
SetSliderOptions(Link, SliderOptions)

child_types = []
SetPossibleTypes(Link, child_types)

