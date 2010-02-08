from apps.plus_groups.models import TgGroup

def patch_groups() :
    for g in TgGroup.objects.all() :
        g.group_type = g.group_type.lower()
        print g.display_name.encode('utf-8'),g.group_type
        g.save()

from apps.plus_permissions.default_agents import get_all_members_group, get_virtual_members_group
from django.conf import settings


def set_type(g, type) :
    g.group_type = type
    print g.display_name, g.group_type
    g.save()

set_type(get_all_members_group(),settings.GROUP_HUB_TYPE)

import ipdb
ipdb.set_trace()
g = get_all_members_group()
g.display_name = settings.ALL_MEMBERS_NAME
g.save()

set_type(get_virtual_members_group(),'internal')

#patch_groups()
