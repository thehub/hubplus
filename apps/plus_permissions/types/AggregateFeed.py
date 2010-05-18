
from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, \
    InterfaceCallProperty, secure_wrap

from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, \
    SetSliderAgents, SetVisibleAgents, SetVisibleTypes, PossibleTypes, SetTypeLabels

from apps.plus_permissions.models import add_type_to_interface_map


from apps.plus_feed.models import AggregateFeed

content_type = AggregateFeed
child_types = []

class AggregateFeedViewer : 
    target = InterfaceReadProperty

UserInterfaces = {
    'Viewer' : AggregateFeedViewer,
    }

add_type_to_interface_map(AggregateFeed, UserInterfaces)

SliderOptions = {'InterfaceOrder':['Viewer'],
                 'InterfaceLabels':{'Viewer':'View'}}

SetSliderOptions(AggregateFeed, SliderOptions)



