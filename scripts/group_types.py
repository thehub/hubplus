import ipdb
import string
from apps.plus_groups.models import TgGroup

def swap(gp,old,new) :
    if gp.group_type == old :
        gp.group_type = new
        gp.save()

ts = set([])
for gp in TgGroup.objects.all() :
    swap(gp,'Hub','Region')
    swap(gp,'group','Interest')
    gp.group_type = string.capwords(gp.group_type)
    gp.save()

    print gp.group_name, gp.group_type
    ts.add(gp.group_type)
    

print ts
