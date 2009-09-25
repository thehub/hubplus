# run from django manage as in 
# python manage.py execfile psn_import/group.py

import pickle
from apps.plus_groups.models import TgGroup
from apps.plus_lib.utils import make_name
from apps.plus_permissions.default_agents import get_admin_user, get_site


def import_group(f_name, group_type) :
    groups = pickle.load(open('mhpss_export/groups.pickle'))
    admin = get_admin_user()
    site = get_site(admin)
    for g in groups:
        print g.keys()
    #print g['groupname'], g['body'], g['description'],g['joinpolicy']
        if g['joinpolicy']== 'open' :
            permission_prototype='public'
        else :
            permission_prototype='private'

        if g['description'] :
            description = g['description']
        elif g['body'] :
            description = g['body']
        else :
            description = 'About this group'

        group_name = make_name(g['groupname'])
        if len(group_name)>30 :
            group_name = group_name[30]
        display_name = g['groupname']
        psn_id = g['uid']

        keywords = g['keywords']

        print group_name, display_name, psn_id, permission_prototype
        print description
        print keywords

        group = site.create_TgGroup(
            group_name = group_name,
            display_name = display_name,
            group_type = group_type ,
            level = 'member',
            user = admin,
            description = description,
            permission_prototype = permission_prototype,
        )
        group.get_inner().psn_id = psn_id
        group.save()

#import_group('mhpss_export/groups.pickle', 'group')
import_group('mhpss_export/hubs.pickle', 'hub')                                                                             

