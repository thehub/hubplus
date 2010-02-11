
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

@json_view
@reply
def on_create_user(request, data) :
    from apps.plus_permissions.types.User import user_post_create
    u = User.objects.plus_get(request.user, username=data['username'])
    if data.has_key('permission_prototype') :
        permission_prototype = data['permission_prototype']
    else :
        permission_prototype = 'public'

    user_post_create(u, permission_prototype)

@json_view
@reply
def on_user_changed(request, data) :
    u = User.objects.plus_get(request.user, username=data['username'])
    u.preferably_pre_save() # normally called pre_save, but must be safe to call post_save (as in this case)
    u.save()
    u.post_save()


@json_view
@reply
def on_create_group(request, data) :
    from apps.plus_permissions.types.TgGroup import group_post_create 
    g = TgGroup.objects.plus_get(request.user, group_id=data['group_id'])
    u = User.objects.plus_get(request.user, username=data['username'])
    if data.has_key('permission_prototype') :
        permission_prototype = data['permission_prototype']
    else :
        permission_prototype = None
    group_post_create(g, u, permission_prototype)


@json_view
@reply
def on_group_changed(request, data) :
    g = TgGroup.objects.plus_get(request.user, group_id=data['group_id'])
    g.post_save()


@json_view
@reply
def on_join_group(request, data) :
    g = TgGroup.objects.plus_get(request.user, group_id=data['group_id'])
    u = User.objects.plus_get(request.user, username=data['username'])
    g.post_join(u)


@json_view
@reply
def on_leave_group(request, data) :
    g = TgGroup.objects.plus_get(request.user, group_id=data['group_id'])
    u = User.objects.plus_get(request.user, username=data['username'])
    g.post_leave(u)

    

