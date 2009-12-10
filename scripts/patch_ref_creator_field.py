
from apps.plus_permissions.default_agents import get_admin_user
from apps.plus_permissions.models import GenericReference

def patch():
    for ref in GenericReference.objects.filter(creator=None):
        ref.creator = get_admin_user()
        ref.save()

patch()

