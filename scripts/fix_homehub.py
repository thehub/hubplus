from apps.profiles.models import Profile
from apps.plus_permissions.default_agents import get_or_create_root_location, get_virtual_members_group

rootloc = get_or_create_root_location()
virtual_members = get_virtual_members_group()

for p in Profile.objects.all() :
    print p.user.username, p.first_name.encode('utf-8'), p.last_name.encode('utf-8'), p.homehub, p.homeplace.name
    if not p.homehub :
        if p.homeplace != rootloc:
            # we can't currently infer from, say, Nepal to Asia
            print "not virtual ... "
        else :
            print "virtual "
            virtual_members.add_member(p.user)
            p.homehub = virtual_members
            p.save()
            p.user.save()
