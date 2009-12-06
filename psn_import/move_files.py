
from psn_import.utils import *

from apps.plus_resources.models import Resource
import ipdb

count = 0
for res in Resource.objects.all() :
    if not res.stub :
        change = "member_resources"
        if 'member_resource' in res.resource.path :
            ipdb.set_trace()
            count = count + 1
            print
            print res.title.encode('utf-8'), res.resource.path
            xs = res.resource.path.split(change)
            pre = xs[0]
            new = 'member_res' + xs[1]
            print "from : "+res.resource.path
            print "to : " + pre + new
            

print count 
