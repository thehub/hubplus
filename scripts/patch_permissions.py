 
from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User

def change_user(user) :
    print user.username, user.get_ref().permission_prototype
    sc = user.get_security_context()
    print sc.get_slider_level('User.Viewer'), sc.get_slider_level('Profile.EmailAddressViewer')
    sc.switch_permission_prototype('public')
    print sc.get_slider_level('User.Viewer'), sc.get_slider_level('Profile.EmailAddressViewer')



if __name__ == '__main__' :
    for u in User.objects.all() :
        if u.username in ['anon','admin'] : continue
        change_user(u)
