# run from django manage as in 
# python manage.py execfile psn_import/group.py

import pickle
from apps.plus_groups.models import TgGroup
from apps.plus_lib.utils import make_name
from apps.plus_permissions.default_agents import get_admin_user, get_site

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
    display_name = g['groupname']
    psn_id = g['uid']

    keywords = g['keywords']

    print group_name, display_name, psn_id, permission_prototype
    print description
    print keywords

    #group = site.create_TgGroup(
    #    group_name = g['groupname'],
    #    display_name = g['groupname'],
    #   group_type = 'interest' ,
    #    level = 'member',
    #    user = admin,
    #    description = self.cleaned_data['description'],
    #    permission_prototype = self.cleaned_data['permissions_set'],
    #    )
    # group.psn_id = g['uid']
    #group.save()
