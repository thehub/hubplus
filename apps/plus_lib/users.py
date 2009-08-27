
from django.contrib.auth.models import User
from apps.plus_permissions.types.User import create_user
from apps.plus_permissions.default_agents import *

def dm(username,email,password) :
    user = create_user(username,email,password)
    user.set_password(password)
    user.save()
    return user

def make_syn():
    try :
        syn1 = dm('synnoveadmin','sf-admin@the-hub.net','synnoveadmin')
    except:
        syn1 = User.objects.get(username='synnoveadmin')
    
    try :
        syn2 = dm('synnovenoadmin','sf-noadmin@the-hub.net', 'synnovenoadmin')
    except :
        syn1 = User.objects.get(username='synnovenoadmin')

    get_all_members_group().add_member(syn1)
    get_all_members_group().add_member(syn2)

    return syn1, syn2

def make_groups() :
    site = get_site(get_admin_user())
    ga = site.create_TgGroup(get_admin_user(), group_name='greenarchitects', display_name='Green Architects', level='member')
    print ga.display_name, ga.id

    ss = site.create_TgGroup(get_admin_user(), group_name='sexysalad', display_name='Sexy Salad Club', level='member')
    print ss.display_name, ss.id


