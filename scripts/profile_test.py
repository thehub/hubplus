import profile

from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User
from apps.plus_permissions.interfaces import secure_wrap

def f() :
    u = User.objects.get(username='phil.jones')
    g = TgGroup.objects.get(group_name='all_members')

    print u, g
    secure_wrap(g,u)

profile.run("f()")
