
from apps.plus_groups.models import TgGroup

from django.conf import settings

for g in TgGroup.objects.all() :
    print g.group_name, g.group_type, g.place.name, g.group_name[-5:]
    if g.group_type == 'hub' :
        g.group_type = settings.GROUP_HUB_TYPE
        g.save()
    
    if g.group_name[-5:]=='hosts':
        g.group_type = 'administrative'
        g.save()

    if g.group_name == settings.VIRTUAL_HUB_NAME :
        g.group_type = settings.GROUP_HUB_TYPE
        g.save()

print settings.GROUP_HUB_TYPE, settings.VIRTUAL_HUB_NAME

from apps.plus_permissions.default_agents import get_all_members_group

alls = get_all_members_group()
admin = alls.get_admin_group()
old_admin = TgGroup.objects.get(id=143)
print "members of alls %s"%len([x for x in alls.get_members()])
print admin.id, admin.group_name
print [x for x in admin.get_members()]
print old_admin.id, old_admin.group_name
print [x for x in old_admin.get_members()]
