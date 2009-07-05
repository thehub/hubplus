
print "apps/plus_permissions/__init__"

from models import get_permission_system

ps = get_permission_system()

# Do this for each content type

from Profile import make_permission_manager

Profile.make_permission_manager()

