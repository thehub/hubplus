
from django.contrib.auth.models import User
from apps.plus_permissions.interfaces import secure_wrap
from apps.plus_lib.counters import Counter
from apps.plus_permissions.default_agents import get_all_members_group

count = Counter()

ed = User.objects.get(username='edmund.colville')
forbidden = set([])
all_members = get_all_members_group()

for u in User.objects.all().order_by('id') :

    #x = raw_input()
    if u.username=='anon' :
        continue
    print 

    print u
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
        
    if not sl :
        print 'no slider level for ', u
        count('no slider level')
        continue

    if not sl.is_user() :
        count('ok')
        print u,sl
        continue

    if sl.username == u.username :
        #print u.id, u.username, u.created, u.is_active
        if u.is_active :
            count('bad, set to self')
        else :
            count('bad, not active')
        continue

    count('ok')



print count
print forbidden
