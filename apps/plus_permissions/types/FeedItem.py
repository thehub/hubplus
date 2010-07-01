from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, \
    InterfaceCallProperty, secure_wrap
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, \
    SetSliderAgents, SetVisibleAgents, SetVisibleTypes, PossibleTypes, SetTypeLabels


from apps.plus_feed.models import FeedItem
from apps.plus_permissions.models import add_type_to_interface_map

content_type = FeedItem
child_types = []

class FeedItemViewer :
    id = InterfaceReadProperty
    short = InterfaceReadProperty
    expanded = InterfaceReadProperty
    external_link = InterfaceReadProperty
    type = InterfaceReadProperty
    target = InterfaceReadProperty
    source = InterfaceReadProperty
    sent = InterfaceReadProperty
    has_avatar = InterfaceCallProperty

UserInterfaces = {
    'Viewer' : FeedItemViewer,
    }

add_type_to_interface_map(FeedItem, UserInterfaces)

SliderOptions = {'InterfaceOrder':['Viewer'], 
                 'InterfaceLabels':{'Viewer':'View'}}

SetSliderOptions(FeedItem, SliderOptions)


