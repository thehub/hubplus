import pickle
from django.contrib.auth.models import User
from apps.plus_permissions.types.User import create_user

from avatar.models import Avatar

from apps.plus_permissions.default_agents import get_or_create_root_location

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
    
    print username, description, fullname, email, biography, roles, portrait

    if not user_exists(username, email) :
        user = create_user(username, email_address=email, password='password')
    else :
        try :
            user = User.objects.get(username=username)
        except :
            user = User.objects.get(email_address=email)
    
    if description : 
        user.description = description
    else :
        user.description = ''
    if biography :
        user.description += '\n'+biography

    if not user.homeplace :
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

    avatar = Avatar()

    user.save()

