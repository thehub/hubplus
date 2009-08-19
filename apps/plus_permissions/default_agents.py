from apps.hubspace_compatibility.models import TgGroup
from django.contrib.auth.models import User

from apps.hubspace_compatibility.models import Location
from django.db import models

def get_or_create_root_location():
    root_location, created = Location.objects.get_or_create(name='HubPlus')
    if created:
        root_location.save()
    return root_location

def get_admin_user():
    try:
        admin_user =  User.objects.filter(username='admin')[0]
    except IndexError:
        admin_user = User(username='admin', email_address='tom.salfield@the-hub.net', password='blah')
        admin_user.save()
    return admin_user

def set_anonymous_group():
    admin_user = get_admin_user()
    return TgGroup.objects.get_or_create(group_name='anonymous', display_name='World', place=get_or_create_root_location(), level='public', user=admin_user)


def get_anonymous_group():
    anonymous_group = TgGroup.objects.filter(group_name="anonymous")
    if not anonymous_group:
        anonymous_group, created = set_anonymous_group()
    return anonymous_group

def set_all_members_group():
    admin_user = get_admin_user()
    return TgGroup.objects.get_or_create(group_name='all_members', display_name='All Members', place=get_or_create_root_location(), level='member', user=admin_user)
           
def get_all_members_group():
    all_members = TgGroup.objects.filter(group_name="all_members")
    if not all_members:
        all_members, created = set_all_members_group()
    return all_members


class CreatorMarker(models.Model) :
    pass


def get_creator_agent() :
    if CreatorMarker.objects.count() > 0 :
        return CreatorMarker.objects.all()[0]
    c = CreatorMarker()
    import ipdb
    ipdb.set_trace()
    c.get_ref()
    c.save()
    return c

