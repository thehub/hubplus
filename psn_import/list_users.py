from psn_import.utils import load_all, maps, reverse, get_user_for

load_all()

for u in maps['User'] :                                                                                                     
    username = u['username']                                                                                                
    pw = u['password']                                                                                                      
    full = u['fullname']
    print username, pw, full, u['uid']

print "len = ",len(maps['User'])
from django.contrib.auth.models import User
print "no users =",User.objects.all().count()

for u in maps['User'] :
    try : 
        get_user_for(u['uid'])
    except :
        print "%s not in Users" % (u['username'])
