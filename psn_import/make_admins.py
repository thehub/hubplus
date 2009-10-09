from django.contrib.auth.models import User
from apps.plus_permissions.default_agents import get_all_members_group

all = get_all_members_group()
hosts = all.get_admin_group()

names = ['jonathanrobinson','alisonstrang','sabine.rakotomalala','ralphonse',
         'jonathan.morgan','lec','Chathuri','brighton','agalappatti',
         #'',''
         ]

for name in names : 
    print name
    try :
        u = User.objects.get(username=name)
        hosts.add_member(u)
        print "%s(%s) added to %s" % (u.get_display_name(),u.username, hosts.get_display_name())
        print u.get_enclosures()
    except :
        print "Don't know a user called %s" % name
