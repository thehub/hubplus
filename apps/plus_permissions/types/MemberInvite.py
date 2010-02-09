# --== Decompile ==--
from apps.plus_permissions.interfaces import InterfaceReadProperty, InterfaceWriteProperty, InterfaceCallProperty, InterfaceReadWriteProperty
from apps.plus_permissions.models import SetSliderOptions, SetAgentDefaults, SetPossibleTypes, SetSliderAgents
from apps.plus_groups.models import MemberInvite
from apps.plus_groups.models import TgGroup
from django.db.models.signals import post_save
import datetime
content_type = MemberInvite
from apps.plus_permissions.default_agents import get_or_create_root_location, get_anonymous_group, get_all_members_group, get_creator_agent
class MemberInviteViewer():
	pk = InterfaceReadProperty
	invited = InterfaceReadProperty
	invited_by = InterfaceReadProperty
	group = InterfaceReadProperty
	message = InterfaceReadProperty
	status = InterfaceReadProperty
	date = InterfaceReadProperty
	is_site_invitation = InterfaceCallProperty


class MemberInviteEditor():
	pk = InterfaceReadWriteProperty
	invited = InterfaceReadWriteProperty
	invited_by = InterfaceReadWriteProperty
	group = InterfaceReadWriteProperty
	message = InterfaceReadWriteProperty
	status = InterfaceReadWriteProperty
	date = InterfaceReadWriteProperty
	is_site_invitation = InterfaceCallProperty


class MemberInviteAccept():
	pk = InterfaceReadProperty
	accept = InterfaceCallProperty
	make_accept_url = InterfaceCallProperty
	status = InterfaceReadWriteProperty
	accepted_by = InterfaceReadWriteProperty
	delete = InterfaceCallProperty


from apps.plus_permissions.models import add_type_to_interface_map
MemberInviteInterfaces = {'Viewer': MemberInviteViewer, 'Editor': MemberInviteEditor, 'Accept': MemberInviteAccept}
add_type_to_interface_map(MemberInvite, MemberInviteInterfaces)
SliderOptions = {'InterfaceOrder': ['Viewer', 'Editor', 'Accept']}
SetSliderOptions(MemberInvite, SliderOptions)
child_types = []
SetPossibleTypes(MemberInvite, child_types)
