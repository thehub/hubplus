from django.contrib.auth.models import User
from apps.plus_permissions.default_agents import get_all_members_group, get_virtual_members_group, get_or_create_root_location

default_home = get_all_members_group()
default_home.location = get_or_create_root_location()

virtual_group = get_virtual_members_group()

def patch_home_hubs() :
    for u in User.objects.all() :
        if (not u.homehub) or (u.homehub == virtual_group):
            u.homehub = default_home
            default_home.join(u)
            if not u.homeplace :
                u.homeplace = u.homehub.location
            print u.username, u.homeplace.name, u.homehub
            u.save()

patch_home_hubs()
