
from django.contrib.auth.models import User
from apps.plus_groups.models import TgGroup
from apps.plus_permissions.interfaces import secure_wrap

from datetime import datetime

uu = User.objects.get(username='p3')
gg = TgGroup.objects.get(id=456)

import ipdb
from apps.plus_lib.redis_lib import redis, CACHE_ON

redis.flushall()
print redis.dbsize()


print
print "Start"
ss = secure_wrap(gg,uu)
print gg.has_member(uu)
print ss._interfaces

print
print "Joining"
gg.add_member(uu)
ss = secure_wrap(gg,uu)
print gg.has_member(uu)
print ss._interfaces

print
print "Leaving"
gg.remove_member(uu)
ipdb.set_trace()
ss = secure_wrap(gg,uu)
print gg.has_member(uu)
print ss._interfaces

print 
print redis.dbsize()

print "multiple secure_wraps with CACHE_ON: ",CACHE_ON

for x in range(10) :
    print x, datetime.now()
    ss = secure_wrap(gg,uu)

