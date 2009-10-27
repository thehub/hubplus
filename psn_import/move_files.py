import sys, os

from apps.plus_resources.models import Resource
import ipdb

ex = set([])
for rs in Resource.objects.all() :
    try :
        print rs.title, rs.in_agent.obj, rs.id
        if not rs.resource :
            print "no resource associated with this"
            continue

        e = rs.get_extension()
        ex.add(e)
        print e
        if e == 'msword' :
            rs.change_extension('doc')
    #ms-excel', 'rtf', 'zip', 'doc', 'msword', 'html', 'ms-powerpoint', 'pdf'
        elif e == 'ms-excel' :
            rs.change_extension('xls')
            
        elif e == 'ms-powerpoint' :
            rs.change_extension('ppt')

    except Exception, e :
        print e
        ipdb.set_trace()

print ex

