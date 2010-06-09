
from apps.profiles.models import Profile

from django.contrib.auth.models import User

from apps.plus_lib.fixes import setup_default_security

def fix(username) :
    u = User.objects.get(username=username)
    setup_default_security(u,'public')


fix('barbara.ruder')
fix('binmann')
