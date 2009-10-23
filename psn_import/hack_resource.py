
from apps.plus_resources.models import Resource
import os, sys
from apps.plus_tags.models import get_tags, tag_delete

for r in Resource.objects.all() :

    if r.created_by : creator = r.created_by.username
    else : creator = 'no created_by'

    print 
    print '%s, %s, %s, %s' % (r.title, creator, r.license, r.in_agent.obj.get_display_name())

    if r.license == 'Copyright 2009, Psychosocial Network' :
        r.license = 'not specified'
        r.save()
     
    tags = get_tags(r)
    for t in tags :
        print t.keyword.encode('utf-8'), t.tag_type, t.tagged_for

    if r.resource :
        print r.resource
        
    else :
        import ipdb
        ipdb.set_trace()
        print "NO RESOURCE"
