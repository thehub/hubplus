
from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User

from apps.plus_lib.parse_json import json_view

def reply(f) :
    def g(*argv, **kwargs) :
        try :
            f(*argv,**kwargs)
            return {'ok':True}
        except Exception, e:
            return {'ok':False,'msg':'%s'%e}
    return g

@json_view
@reply
def on_user_create(request, data) :
    from apps.plus_permissions.types.User import user_post_create
    u = User.objects.plus_get(request.user, username=data['username'])
    
    if user.active:
        if user.public_field:
            permission_prototype = 'public'
        else :
            permission_prototype = 'members_only'
    else :
        permission_prototype = 'inactive'
        
        # inactive users should NOT be public... 
        if user.public_field:
            user.public_field = 0
        
    user_post_create(u, permission_prototype)


@json_view
@reply
def on_user_change(request, data) :
    print "in on_user_changed"
    u = User.objects.plus_get(request.user, username=data['username'])
    u.preferably_pre_save() # normally called pre_save, but must be safe to call post_save (as in this case)
    u.save()
    u.post_save()
    print "user %s was changed by an external application" % u.username


@json_view
@reply
def on_group_join(request, data) :
    g = TgGroup.objects.plus_get(request.user, id=data['group_id'])
    u = User.objects.plus_get(request.user, username=data['username'])
    g.post_join(u)


@json_view
@reply
def on_group_leave(request, data) :
    g = TgGroup.objects.plus_get(request.user, id=data['group_id'])
    u = User.objects.plus_get(request.user, username=data['username'])
    g.post_leave(u)

    

