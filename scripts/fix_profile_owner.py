
from apps.profiles.models import Profile

from django.contrib.auth.models import User

from apps.plus_lib.fixes import ensure_user_has_permission_on_self

def fix(username) :
    u = User.objects.get(username=username)
    ensure_user_has_permission_on_self(u)


fix('barbara.ruder')
fix('binmann')
