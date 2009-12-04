from apps.plus_permissions.default_agents import get_all_members_group

all =get_all_members_group()
from django.conf import settings
all.display_name = settings.ALL_MEMBERS_NAME
all.save()
