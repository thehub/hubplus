import sys

from psn_import.utils import maps, reverse, load_file, list_type, get_top_container, load_all, psn_group_name

from apps.plus_groups.models import TgGroup

import ipdb

load_all()

for t in TgGroup.objects.all() :
    #print t.description.encode('utf-8')
    if "Nutr" in t.get_display_name() :

        print 
        print t.id, t.group_name
        print t.description
        print t.psn_id, t.get_display_name()
        for m in t.get_members() :
            print m


for g in maps['Group'] :
    if "Nutr" in g['groupname'] :
        print
        print g['groupname'],g['uid']
        print g
    if "etwork" in g['groupname'] :

        print 
        print g['groupname'],g['uid']
        print g



def update(obj, d): 
    obj.title = d['groupname']
    obj.group_name = psn_group_name(obj.title)
    obj.psn_id = d['uid']
    obj.description = d['body']

    print "--"
    print obj.id, obj.title, obj.group_name, obj.psn_id
    print obj.description
    #obj.save()
    print "++"


nut = TgGroup.objects.get(id=76)
print nut.id, nut.psn_id, nut.title, nut.group_name

net = TgGroup.objects.get(id=4)
print net.id, net.psn_id, net.title, net.group_name
