
from apps.plus_groups.models import TgGroup

scs = {}
for g in TgGroup.objects.all().order_by('id') :
    print g.display_name, g.id,
    try : 
        sc = g.get_security_context() 
        print "sc:%s"%sc.id,
        if sc in scs.keys() :
            print "!!! shared sc with %s" % scs[sc],

    except :
        print "*** no security context",
    try :
        admin = g.get_admin_group()
        print admin.id
    except :
        print "*** problem getting admin group ***"


