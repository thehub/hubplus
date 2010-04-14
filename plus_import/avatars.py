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
 
    new_avatar = Avatar(
        target = u.get_ref(),
        primary = True,
        avatar = path,
        )

    avatars = Avatar.objects.filter(target=u).order_by('-primary')
 
    if avatars :    
        old_avatar = avatars[0]
        #if old_avatar.avatar.size == new_avatar.avatar.size :
        #    print "exists"
        #    continue

    #import ipdb
    #ipdb.set_trace()
    print avatars, new_avatar

    new_avatar.save()
    new_file = new_avatar.avatar.storage.save(path, f)
    new_avatar.save()
   

