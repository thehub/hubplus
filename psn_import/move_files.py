import sys, os

from apps.plus_resources.models import Resource

ex = set([])
for r in Resource.objects.all() :
    print r.title, r.in_agent.obj, r.id
    e = r.get_extension()
    ex.add(e)
    print e
    if e == 'msword' :
        r.change_extension('doc')
    #ms-excel', 'rtf', 'zip', 'doc', 'msword', 'html', 'ms-powerpoint', 'pdf'
    elif e == 'ms-excel' :
        r.change_extension('xls')

    elif e == 'ms-powerpoint' :
        r.change_extension('ppt')

print ex

