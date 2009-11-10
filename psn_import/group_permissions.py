 
from apps.plus_groups.models import TgGroup
from psn_import.utils import maps, reverse, load_all
import ipdb

def change(group, new_type) :
    print group.group_name
    print group.get_ref().permission_prototype

    sc = group.get_security_context()
    print sc.get_slider_level('TgGroup.Viewer'), sc.get_slider_level('WikiPage.Viewer'), sc.get_slider_level('TgGroup.Invite')

    sc.switch_permission_prototype(new_type)
    
    print group.get_ref().permission_prototype
    print sc.get_slider_level('TgGroup.Viewer'), sc.get_slider_level('WikiPage.Viewer'), sc.get_slider_level('TgGroup.Invite')


if __name__ == '__main__' :
    load_all()
    for g in maps['Group'] :
        group = TgGroup.objects.get(psn_id=g['uid'])
        print group
        print g['groupname'],g['joinpolicy']
        if g['joinpolicy'] == 'open' :
            change(group,'public')
        elif g['joinpolicy'] == 'closed' :
            change(group,'private')
        else :
            ipdb.set_trace()

