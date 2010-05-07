
from django.contrib.auth.models import User
from apps.plus_permissions.models import SecurityContext, SecurityTag
from apps.plus_permissions.default_agents import get_all_members_group
from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User

all_members = get_all_members_group()
site_admin = all_members.get_admin_group()
site_admin_ref = site_admin.get_ref()

old_admin = TgGroup.objects.get(id=148)
old_admin_ref = old_admin.get_ref()
phil = User.objects.get(username='phil.jones')

def fix_all() :
    for u in User.objects.all() :
        try :
            sc = u.get_security_context()
        except Exception, e:
            print u.username, " problem with Security Context"
            continue
        #fix_tags(u,sc)
        fix_sliders(u,sc)
        
def fix_tags(u,sc) :
    for tag in SecurityTag.objects.filter(security_context=sc):
        #print tag.interface, [x.obj for x in tag.agents.all()]
        if not site_admin.get_ref().id in [x.id for x in tag.agents.all()] :
            print u.username, tag.interface, ' missing real admin' 
            tag.add_agents([site_admin.get_ref()])
        if old_admin.get_ref().id in [x.id for x in tag.agents.all()] :
            print u.username, tag.interface, ' has old admin'
            tag.remove_agents([old_admin.get_ref()])
                

def fix_sliders(u,sc) :

    if sc.context_admin.id == old_admin_ref.id :
        sc.context_admin = site_admin_ref
        sc.save()
        print "***",
        print u, sc.context_admin.obj, sc.context_agent.obj        
    elif sc.context_admin.id != site_admin_ref.id :
        print "*",
        print u, sc.context_admin.obj, sc.context_agent.obj

fix_all()




