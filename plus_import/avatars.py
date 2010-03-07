from __future__ import with_statement

import pickle
from django.contrib.auth.models import User

from avatar.models import Avatar, avatar_file_path

from django.core.files.images import ImageFile
from apps.plus_groups.models import Location

for u in User.objects.all() :
    f_name = 'hubplus_avatars/binaries/user-%s'%u.id
    try:
        f = ImageFile(open(f_name),'rb')
    except Exception :
        print "no file for %s, %s, %s" % (u.username,u.id,f_name)
        continue

    print "found one %s" % u.username

    path = avatar_file_path(target=u, filename=u.username)
 
    avatar = Avatar(
        target = u.get_ref(),
        primary = True,
        avatar = path,
        )

    avatar.save()
    new_file = avatar.avatar.storage.save(path, f)
    avatar.save()
   

