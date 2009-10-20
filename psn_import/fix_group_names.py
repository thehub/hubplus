
from apps.plus_groups.models import TgGroup
from apps.plus_lib.utils import make_name
from psn_import.utils import psn_group_name


for g in TgGroup.objects.filter(level='member') :
    print g.id, g.display_name, g.group_name

    group_name = psn_group_name(g.display_name)

    a = g.get_admin_group()

    g.group_name = psn_group_name(group_name)
    print "new group", g.group_name
    g.save()
    a.group_name = psn_group_name(g.display_name+" Hosts")
    print "new admin", a.group_name
    a.save()
    
