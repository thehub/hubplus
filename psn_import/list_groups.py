import sys

from psn_import.utils import maps, reverse, load_file, list_type, get_top_container, load_all

from apps.plus_groups.models import TgGroup

load_all()

for t in TgGroup.objects.all() :
    print t.description.encode('utf-8')
    if "Nutr" in t.get_display_name() :
        print 
        print t.id, t.group_name
        print t.description
        print t.psn_id, t.get_display_name()
        for m in t.get_members() :
            print m


for g in maps['Group'] :
    if "Nutr" in g['groupname'] :
        print g['groupname']
        print g
    if "etwork" in g['groupname'] :
        print g['groupname']
        print g

