from apps.plus_resources.models import Resource
from apps.plus_groups.models import TgGroup
from apps.plus_tags.models import Tag, get_tags

import ipdb
res = Resource.objects.all()[0]

ipdb.set_trace()

res =  Resource.objects.all()
print res
for r in res : 
    print r, r.title.encode('utf-8'), r.created_by
