from django.contrib.auth.models import User
from apps.plus_permissions.default_agents import get_all_members_group, get_virtual_members_group

all_members = get_all_members_group()
default_home = get_virtual_members_group()
def patch_home_hubs() :
    for u in User.objects.all() :
        if (not u.homehub) or (u.homehub == all_members):
            u.homehub = default_home
            default_home.join(u)
            print u.username, u.homeplace, u.homehub
            u.save()

patch_home_hubs()
