import sys

from psn_import.utils import maps, reverse, load_file, list_type, get_top_container, load_all, psn_group_name

from apps.plus_groups.models import TgGroup

import ipdb

load_all()

nut_d = reverse['f25a270c720819a2fede04e760499808'][1]
print
print nut_d['groupname'],nut_d['uid']
print nut_d

net_d = reverse['712ffffffffffffffffffffffffffffff'][1]
print
print net_d['groupname'],net_d['uid']
print net_d 

def update(obj, d): 
    obj.display_name = d['groupname']
    obj.group_name = psn_group_name(obj.display_name)
    obj.psn_id = d['uid']
    obj.description = d['body']

    print "--"
    print obj.id, obj.title, obj.group_name, obj.psn_id
    print obj.description
    obj.save()
    print "++"


print
nut = TgGroup.objects.get(id=76)
print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
update(nut,nut_d)

net = TgGroup.objects.get(id=4)
update(net,net_d)

from apps.plus_tags.models import TagItem
nut_tags = TagItem.objects.filter(ref=nut.get_ref())
net_tags = TagItem.objects.filter(ref=net.get_ref())

print "nut_tags"
print [(n.ref.obj, n.keyword) for n in nut_tags]

print "net_tags"
for n in net_tags :
    print n.ref.obj, n.keyword
    n.ref = nut.get_ref()
    print "*",n.ref.obj, n.keyword
    n.save()

