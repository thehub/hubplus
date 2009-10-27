

from apps.avatar.models import Avatar

for a in Avatar.objects.all() :
    if not a.target:
        a.target = a.user.get_ref()
        print a.user, a.target.obj
        a.save()
