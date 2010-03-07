
from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User

from apps.plus_lib.parse_json import json_view

def reply(f) :
    def g(*argv, **kwargs) :
        try :
            f(*argv,**kwargs)
            return {'ok':True}
        except Exception, e:
            return {'ok':False,'msg':'%s;; %s'%(e,e.__class__.__name__)}
    return g

@json_view
@reply
def on_user_add(request, data) :

    from apps.plus_permissions.types.User import user_post_create

    # XXX can't do a plus_get yet because all the other permissioning 
    # infrastructure hasn't been created, but we need to test some kind of 
    # permission here
    user = User.objects.get(id=data['id'])

    if user.user_name and not user.username :
        user.username = user.user_name

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
        
    user_post_create(user, permission_prototype)


@json_view
@reply
def on_user_change(request, data) :
    print "in on_user_changed"
    u = User.objects.plus_get(request.user, id=data['id'])

    if not u.homehub or u.homehub.place != u.homeplace :
        from apps.plus_permissions.default_agents import get_or_create_root_location, get_all_members_group
        if u.homeplace == get_or_create_root_location() :
            u.homehub = get_all_members_group()
        else :
            u.homehub = TgGroup.objects.get(place=u.homeplace,level='member')

    u.save()
    u.post_save()
    print "user %s was changed by an external application" % u.username


@json_view
@reply
def on_group_join(request, data) :
    g = TgGroup.objects.plus_get(request.user, id=data['group_id'])
    u = User.objects.plus_get(request.user, id=data['user_id'])
    g.post_join(u)


@json_view
@reply
def on_group_leave(request, data) :
    g = TgGroup.objects.plus_get(request.user, id=data['group_id'])
    u = User.objects.plus_get(request.user, id=data['user_id'])
    g.post_leave(u)

    

