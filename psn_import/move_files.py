
from psn_import.utils import *

from apps.plus_resources.models import Resource
import ipdb
import re
count = 0
for res in Resource.objects.all() :
    if not res.stub :
        sep = "_media/"
        if 'member_resource' in res.resource.path :
            
            count = count + 1
            print
            print res.name, res.title.encode('utf-8')
            print res.resource.path
            xs = res.resource.path.split(sep)
            pre = xs[0]
            post = xs[1]
            new_post = re.sub('member_resources','member_res',post)
            print "from : "+res.resource.path
            print "to : " + pre + sep + new_post
            res.rename_file(new_post, sep)

print count 
