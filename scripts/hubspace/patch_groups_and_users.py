from apps.plus_groups.models import TgGroup
from apps.plus_permissions.types.TgGroup import setup_group_security
from apps.plus_permissions.default_agents import get_admin_user, get_all_members_group, get_or_create_root_location
from apps.plus_permissions.views import setup_hubs_security, create_reference
from django.contrib.auth.models import User
from apps.plus_permissions.types.User import setup_user_security

from apps.plus_permissions.default_agents import get_or_create_root_location, get_virtual_members_group

from apps.plus_groups.models import TgGroup
from apps.plus_permissions.default_agents import get_or_create_root_location, get_admin_user
from apps.plus_permissions.types.Profile import ProfileInterfaces


def give_host_permissions(hub):
    """give hosts all rights to on user profiles of their members
    """
    admin = get_admin_user()
    for member in hub.get_members():
        for prof in ProfileInterfaces:
            member.get_security_context().add_arbitrary_agent(hub.get_admin_group(), 'Profile.%s' % prof, admin)



def tidy_groups():
    hub_host_groups = TgGroup.objects.filter(level__in=['host', 'director'])
    for hub in hub_host_groups:
        display_name = hub.display_name.title().replace('Host', 'Hosts').replace('Director', 'Directors')
        hub.group_name = hub.group_name.lower().strip().replace(' ', '')
        if hub.id in [1,2,3]:
            hub.display_name = display_name.replace('London', 'Islington')
        hub.save()
        
    
    hub_members_groups = TgGroup.objects.filter(level='member')
    for hub in hub_members_groups:
        hub.group_name = hub.group_name.replace('_member', '').replace(' ', '').strip().lower()
        hub.display_name = hub.group_name.replace('_', ' ').replace('member', '').strip().title()
        if not hub.display_name:
            hub.display_name = hub.group_name.title()
        hub.group_type = 'hub'
        hub.save()
        give_host_permissions(hub)
        

def patch_in_groups():
    """Do group security setup for hubspace groups

       XXX patch group names to reflect Location names      
       XXX ensure all directors are in the host group 
       1. setup a security context for each group passing in context_agent, context_admin and creator 
    2. set 'hosts' as a members of the members group, ignore 'directors' groups (they are deprecated - bring on host anarchy

    """
    no_security = [group for group in TgGroup.objects.filter(level='member') if not group.ref.all()]
    admin_user = get_admin_user()
    for group in no_security:
        setup_hubs_security(group, admin_user)
    
    #this should have setup most of the host groups, but if not
    no_security_host = [group for group in TgGroup.objects.filter(level='host') if not group.ref.all()]

    for group in no_security_host:
        create_reference(TgGroup, group)
        setup_group_security(group, group, group, admin_user, 'private')

    print "patched %s hub group's security" % str(len(no_security_host))


def patch_in_profiles():
    """create profiles and setup security hubspace users 
    """
    site_members_group = get_all_members_group()
    all_members_hosts = site_members_group.get_admin_group()
    site_members = site_members_group.users.all()
    root_location = get_or_create_root_location()
    
    def patch_user(user):
        print "%s at %s" % (user.username, user.homeplace)
        
        if user not in site_members and user.username != 'anon':
            site_members_group.users.add(user)
        if user.homeplace:
            user.homehub = user.homeplace.tggroup_set.get(level='member')
        else:
            user.homeplace = root_location
            user.homehub = site_members_group
        
        user.save()
        create_reference(User, user)

        if user.active:
            if user.public_field:
                setup_user_security(user,'public')
            else:
                setup_user_security(user,'members_only')
        else:
            setup_user_security(user,'inactive')
            # inactive users should NOT be public...
            if user.public_field:
                user.public_field = 0
                user.save()

        if not user.hostinfo_set.count():
            hi = user.create_HostInfo(user, user=user)
            hi.save()

        if not user.public_field:
            user.public_field = 0 # its sometimes NULL atm
        user.save()
        profile = user.create_Profile(user, user=user)
        profile.save()

    users = User.objects.all().order_by('id')
    cnt = User.objects.count()
    batch_size = 50
    start = 0
    end = 50
    all = set([])
    def process_user_slice(users):
        for user in users:    
            patch_user(user)

    from threading import Thread
    while True:
        # memory wasn't getting released in the loop...no idea why, so I decided to batch it in 100 user threads which we wait to rejoin before processing another batch...appears to work in keeping mem usage down
        t = Thread(target=process_user_slice, args=[users[start:end]])
        t.start()
        t.join()
        if end == cnt:
            break
        start = end
        end = min(end + batch_size, cnt)

    print "patched %s users to have profiles" % str(users.count())


def individual_changes():
    # make admin user active
    admin = get_admin_user()
    admin.active = True
    admin.save()

    # 

def main():
    patch_in_groups()
    patch_in_profiles()
    tidy_groups()
    individual_changes()

if __name__ == '__main__':
    main()
