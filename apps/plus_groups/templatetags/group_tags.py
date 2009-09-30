from django import template
from apps.plus_permissions.api import TemplateSecureWrapper
from apps.plus_lib.utils import hub_name

register = template.Library()

def show_group(request, group):
    group = TemplateSecureWrapper(group)
    no_of_members = group.get_no_members()
    if group.place.name == 'HubPlus':
        group_label = "group"
    else:
        group_label = hub_name().lower()
    return {"group": group, "no_of_members":no_of_members, "group_label":group_label}
register.inclusion_tag("group_item.html")(show_group)



