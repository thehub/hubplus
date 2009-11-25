from apps.plus_groups.models import TgGroup
from apps.plus_permissions.default_agents import get_admin_user, get_all_members_group, get_or_create_root_location
from apps.plus_permissions.views import setup_hubs_security, create_reference, setup_group_security
from django.contrib.auth.models import User
from apps.plus_permissions.types.User import setup_user_security

def patch_in_groups():
    """Do group security setup for hubspace groups

       XXX patch group names to reflect Location names      
       XXX ensure all directors are in the host group 
       1. setup a security context for each group passing in context_agent, context_admin and creator 
    2. set 'hosts' as a members of the members group, ignore 'directors' groups (they are deprecated - bring on host anarchy

    """
    no_security = [group for group in TgGroup.objects.filter(level='member').exclude(place__name='hubplus') if not group.ref.all()]
    admin_user = get_admin_user()
    for group in no_security:
        setup_hubs_security(group, admin_user)
    
    #this should have setup most of the host groups, but if not
    no_security_host = [group for group in TgGroup.objects.filter(level='host') if not group.ref.all()]

    for group in no_security_host:
        create_reference(TgGroup, group)
        setup_group_security(group, group, group, admin_user)

    print "patched %s hub group's security" % str(len(no_security_host))


def patch_in_profiles():
    """create profiles and setup security hubspace users 
    """

    site_members_group = get_all_members_group()
    site_members = site_members_group.users.all()

    users = User.objects.all()
    for user in users:
        if user not in site_members and user.username != 'anon':
            site_members_group.users.add(user)
        if not user.homeplace :
            user.homeplace = get_or_create_root_location()
            user.save()
            print "%s at %s" % (user.username, user.homeplace)

    users = User.objects.filter(profile__isnull=True)
    no_of_users = users.count()

    for user in users:
        print user.username
        create_reference(User, user)
        setup_user_security(user,'public')
        profile = user.create_Profile(user, user=user)
        profile.save()
        print `profile`

    print "patched %s users to have profiles" % str(no_of_users)

    users = User.objects.filter(hostinfo__isnull=True)
    no_of_users = users.count()

    for user in users:
        print user.username
        hi = user.create_HostInfo(user, user=user)
        hi.save()
        print `hi`

    print "patched %s users to have host_info" % str(no_of_users)


patch_in_groups()
patch_in_profiles()
