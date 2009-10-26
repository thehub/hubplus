from __future__ import with_statement

import pickle
from django.contrib.auth.models import User
from apps.plus_permissions.types.User import create_user

from apps.plus_permissions.default_agents import get_or_create_root_location
from avatar.models import Avatar, avatar_file_path

from django.core.files.images import ImageFile
from apps.plus_groups.models import Location

def user_exists(username, email) :
    if User.objects.filter(username=username) : return True
    if User.objects.filter(email_address=email) : return True
    return False


users = pickle.load(open('mhpss_export/users.pickle'))
for u in users:    
    print u
    username = u['username']
    description = u['description']
    roles = u['roles']
    fullname = u['fullname'].strip()
    biography = u['biography']
    email = u['email']
    portrait = u['portraitfile'].split('/')[-1]
    psn_id = u['uid']
    location = u['location']
    
    print username, description, fullname, email, biography, roles, portrait, psn_id

    if not user_exists(username, email) :
        user = create_user(username, email_address=email, password='password')
    else :
        try :
            user = User.objects.get(username=username)
        except :
            user = User.objects.get(email_address=email)
    
    user.set_password('password')
    if description : 
        user.description = description
    elif biography :
        user.description = biography

    if not user.homeplace :
        if location :
            p,flag = Location.objects.get_or_create(name=location)
            user.homeplace = p
        else :
            user.homeplace = get_or_create_root_location()
    
    if " " in fullname :
        first, last = fullname.rsplit(' ',1)
    elif "." in fullname :
        first, last = fullname.rsplit('.',1)
    else :
        first = fullname
        last = ''        

    user.first_name = first[:30]
    user.last_name = last[:30]
    user.psn_id = psn_id

    user.save()

    f = ImageFile(open('mhpss_export/user_images/%s'%portrait),'rb')
    if f.size == 1357 :
        continue # image is plone default ... we don't want it

    path = avatar_file_path(target=user, filename=portrait)
 
    avatar = Avatar(
        target = user.get_ref(),
        primary = True,
        avatar = path,
        )

    avatar.save()

    new_file = avatar.avatar.storage.save(path, f)
    avatar.save()
   

