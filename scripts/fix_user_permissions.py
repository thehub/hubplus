
from django.contrib.auth.models import User
from apps.plus_permissions.interfaces import secure_wrap
from apps.plus_lib.counters import Counter
from apps.plus_permissions.default_agents import get_all_members_group
from apps.plus_permissions.models import permissions_failures_for

count = Counter()

ed = User.objects.get(username='edmund.colville')
forbidden = set([])
all_members = get_all_members_group()

def test_permissions() :
    for u in permissions_failures_for(ed) :
        if u.username == 'anon' : 
            continue
        try :
            print u.id, u, u.active, u.is_active, u.created, u.homeplace.name, u.homehub, u.get_ref().permission_prototype
        except Exception,e :
            print e

test_permissions()

def fix_permissions() :

    for u in permissions_failures_for(ed) :
        if u.username=='anon' :
            continue

        try :
            sc = u.get_security_context()
            print "tags ",sc.get_tags_for_interface('User.Viewer')
            sl = u.get_slider_level('User.Viewer')
        except Exception, e:
            print "ERROR"
            print e
            continue

        su = secure_wrap(u,ed)
        print "ed's access",su._interfaces
    
        try:
            su.username 
        except Exception :
            print "**excluded**"
            forbidden.add(u)
            sc.move_slider(all_members.get_ref(),'User.Viewer',skip_validation=True,no_user=True)
    
    
        sp = secure_wrap(u.get_profile(),ed)
        try :
            print "ed's access to profile",sp._interfaces
            sp.username
        except Exception :
            print "*** profile excluded"
            sc.move_slider(all_members.get_ref(),'Profile.Viewer',skip_validation=True,no_user=True)
        

    print forbidden
