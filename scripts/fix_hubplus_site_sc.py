
from apps.plus_groups.models import TgGroup
from apps.plus_permissions.default_agents import get_all_members_group, get_site
from django.contrib.auth.models import User
from apps.plus_permissions.site import Site

alls = get_all_members_group()
site_admins = alls.get_admin_group()



def fix_hosts_membership() :
    # the all members hosts group needs to be a member of all
    # the other hosting groups


    g = TgGroup.objects.get(id=187)
#    for u in 
#recipients set([<User: yuliya>])

    #for u in ['salfield', 'j.robinson', 'meera.deepak', 'soledad.pons', 'benedikte.koldingsnes', 'emily.dent', 'fgodat', 'phil.jones'] : g.add_member(u)

    for h in TgGroup.objects.filter(group_type = 'member') :
        print h.id, h,
        print [(x.id, x.get_display_name()) for x in h.get_members()]
        #h.add_member(site_admins)
        


def fix_site() :
    
    phil = User.objects.get(username='phil.jones')
    
    site  = Site.objects.all()[0]
    site.save()

    alls = get_all_members_group()
    sa = alls.get_admin_group()

    import ipdb
    ipdb.set_trace()
    
    print site.get_security_context().id, site.get_security_context().get_target().id
    print sa,sa.id,sa.get_security_context().id, sa.get_security_context().get_target(), sa.get_security_context().get_target().id


    site.acquires_from(sa)
    sc=site.create_custom_security_context()

    ref = site.get_ref()
    ref.acquired_scontext = None
    ref.save()

    site.acquires_from(sa)   
    sc=site.use_acquired_security_context()
    print site.get_security_context().id, site.get_security_context().get_target().id


if __name__ == '__main__' :
    fix_site()
