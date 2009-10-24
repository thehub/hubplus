# run from django manage as in 
# python manage.py execfile psn_import/group.py

import pickle
from apps.plus_groups.models import TgGroup, Location
from apps.plus_lib.utils import make_name
from apps.plus_permissions.default_agents import get_admin_user, get_site, get_or_create_root_location
from psn_import.utils import psn_group_name

root = get_or_create_root_location()

def import_group(f_name, group_type, fn_place) :
    groups = pickle.load(open(f_name))
    admin = get_admin_user()
    site = get_site(admin)
    for g in groups:
        #print g.keys()
        print g['groupname'], g['body'], g['description'],g['joinpolicy']

        if g['joinpolicy']== 'open' :
            permission_prototype='public'
        else :
            permission_prototype='private'

        description = ""
        if g['description'] :
            description = description + g['description']
        if g['body'] :
            description = description + g['body']
        if description == "" :
            description = 'About this group'

        display_name = g['groupname']
        group_name = psn_group_name(display_name)
        psn_id = g['uid']

        keywords = g['keywords']

        print group_name, display_name, psn_id, permission_prototype
        print description
        print keywords

        groups = TgGroup.objects.filter(psn_id=psn_id)
        if groups : 
            group = groups[0]
        else :
            group = site.create_TgGroup(
                group_name = group_name,
                display_name = display_name,
                group_type = group_type ,
                level = 'member',
                user = admin,
                description = description,
                permission_prototype = permission_prototype,
                )
            group = group.get_inner()

        group.psn_id = psn_id
        group.group_name = group_name
        
        group.place = fn_place(g)
        
        group.save()
        print "XX ", group.display_name

def group_place(dict) :
    return get_or_create_root_location()

import_group('mhpss_export/groups.pickle', 'group', group_place)


def region_place(dict) :
    name= dict['location']
    if name == '' :
        name = dict['groupname']
    if Location.objects.filter(name=name).count() > 0 :
        return Location.objects.get(name=name)
    l = Location(name=name)
    l.save()
    return l

import_group('mhpss_export/hubs.pickle', 'Hub',region_place)


for g in TgGroup.objects.all() :
    if g.place.id != root.id and g.level == 'member' :

        admin = g.get_admin_group()
        admin.place = g.place
        admin.save()

