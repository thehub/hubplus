from apps.profiles.models import Profile, HostInfo
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents
from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty

content_type = HostInfo
child_types = []
SetPossibleTypes(HostInfo, child_types)

class HostInfoViewer :
    user = InterfaceReadProperty
    find_out = InterfaceReadProperty
    peer_mentoring = InterfaceReadProperty
    expected_membership_benefits = InterfaceReadProperty
    project = InterfaceReadProperty
    project_stage = InterfaceReadProperty
    assistance_offered = InterfaceReadProperty

class HostInfoEditor :
    find_out = InterfaceWriteProperty
    peer_mentoring = InterfaceWriteProperty
    expected_membership_benefits = InterfaceWriteProperty
    project = InterfaceWriteProperty
    project_stage = InterfaceWriteProperty
    assistance_offered = InterfaceWriteProperty

from apps.plus_permissions.models import add_type_to_interface_map

HostInfoInterfaces = {'Viewer': HostInfoViewer,
                     'Editor': HostInfoEditor,
                      }


add_type_to_interface_map(HostInfo, HostInfoInterfaces)

SliderOptions = {'InterfaceOrder':['Viewer'], 'InterfaceLabels':{'Viewer':'View', 'Editor':'Edit'}}
SetSliderOptions(HostInfo, SliderOptions)




