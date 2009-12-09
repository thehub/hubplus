 
from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User

def change_user(user) :
    print user.username, user.get_ref().permission_prototype
    sc = user.get_security_context()
    print sc.get_slider_level('User.Viewer'), sc.get_slider_level('Profile.EmailAddressViewer')
    sc.switch_permission_prototype('public')
    print sc.get_slider_level('User.Viewer'), sc.get_slider_level('Profile.EmailAddressViewer')


def change_group(group) :
    pp = group.get_ref().permission_prototype
    if pp == 'private' :
        print group.id, group.group_name, group.get_ref().permission_prototype

        sc = group.get_security_context()
    
        print sc.get_slider_level('TgGroup.Viewer'), sc.get_slider_level('WikiPage.Viewer')
    
        sc.switch_permission_prototype(group.get_ref().permission_prototype)
        print sc.get_slider_level('TgGroup.Viewer'), sc.get_slider_level('WikiPage.Viewer')

import ipdb

if __name__ == '__main__' :
    for u in User.objects.all() :
        if u.username in ['anon','admin'] : continue
        #change_user(u)
    
    for g in TgGroup.objects.all() :
        try:
            change_group(g)
        except :
            ipdb.set_trace()
