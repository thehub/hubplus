

def ensure_user_has_permission_on_self(user):
    p = user.get_profile()
    print p,p.user.username, p.get_ref().creator
    def pif(i) :
        print i, p.get_agents_for_interface(i)

    sc = p.get_security_context()

    if user not in p.get_agents_for_interface('Profile.Viewer') :
        pif('Profile.Viewer')
        sc.move_slider(user,'Profile.Viewer',no_user=True)
        pif('Profile.Viewer')
    
    if user not in p.get_agents_for_interface('Profile.Editor') :
        pif('Profile.Editor')
        sc.move_slider(user,'Profile.Editor',no_user=True)
        pif('Profile.Editor')
