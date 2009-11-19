from django.contrib.auth.models import User

def patch_user_permission_default(user) :
    print user.username, user.get_ref().permission_prototype, 

    sc = user.get_security_context()
    print sc.get_target()
    print sc.get_slider_level('User.Viewer'), sc.get_slider_level('Profile.Editor')

    sc.switch_permission_prototype('public')
    print user.get_ref().permission_prototype
    print sc.get_slider_level('User.Viewer'), sc.get_slider_level('Profile.Editor'), sc.get_slider_level('HostInfo.Viewer')

if __name__ == '__main__' :
    for u in User.objects.all() :
        if u.username=='anon' : continue
        patch_user_permission_default(u)
