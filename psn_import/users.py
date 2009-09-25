import pickle
from django.contrib.auth.models import User
from apps.plus_permissions.types.User import create_user

def user_exists(username, email) :
    if User.objects.filter(username=username) : return True
    if User.objects.filter(email_address=email) : return True
    return False

users = pickle.load(open('mhpss_export/users.pickle'))
for u in users:    
    username = u['username']
    description = u['description']
    roles = u['roles']
    fullname = u['fullname']
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
        print "DESCRIPTION"
        print description

        user.description = description
    elif biography :
        user.description = biography
    user.save()

