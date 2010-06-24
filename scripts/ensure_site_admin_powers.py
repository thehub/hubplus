
from apps.plus_groups.models import TgGroup

from apps.plus_permissions.default_agents import get_all_members_group

all_members = get_all_members_group()
site_admin = all_members.get_admin_group()

for g in TgGroup.objects.hubs().all() :
    hosts = g.get_admin_group()
    print g, [x for x in hosts.get_members()]
    if site_admin not in hosts.get_members() :
        print "BANG"
        
