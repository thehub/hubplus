from django.contrib.auth.models import User


def on_user_add(user_id) :

    from apps.plus_permissions.types.User import user_post_create

    # XXX can't do a plus_get yet because all the other permissioning 
    # infrastructure hasn't been created, but we need to test some kind of 
    # permission here
    user = User.objects.get(id=user_id)

    if user.user_name and not user.username :
        user.username = user.user_name

    if user.active:
        if user.public_field:
            permission_prototype = 'public'
        else :
            permission_prototype = 'members_only'
    else :
        permission_prototype = 'inactive'
        
        if user.public_field:
            user.public_field = 0
        
    user_post_create(user, permission_prototype)

if __name__ == '__main__' :
    on_user_add(6458)
