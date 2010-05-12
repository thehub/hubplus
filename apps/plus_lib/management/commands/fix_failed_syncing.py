from django.contrib.auth.models import User

import sys
from django.utils import termcolors
from django.core.management.base import NoArgsCommand

style = termcolors.make_style(fg='green', opts=('bold',))

# XXX copied from apps.synced.views ... maybe refactor at some point
def on_user_add(user_id) :
    from apps.plus_permissions.types.User import user_post_create
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


class Command(NoArgsCommand):
    help = """Fixes issues due to syncer failure. 
At the moment, failure on hubspace creating users
which leads to them not having Profiles or usernames etc."""
    args = ''
    requires_model_validation = False

    def handle_noargs(self, **options):
 
        for user in User.objects.all() :
            if user.user_name=='anon' :
                continue
            try :
                user.get_profile()
            except Exception, e:
                print user.id,
                on_user_add(user.id)
                user = User.objects.get(id=user.id)
                print user.username

