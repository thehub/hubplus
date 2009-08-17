from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User, UserManager, check_password

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.hubspace_compatibility.models import TgGroup, Location


import datetime


# Group types
HUB     = 'HUB'
GROUP   = 'GROUP'
MEMBERS = 'MEMBERS'
HOSTS   = 'HOSTS'

def extract(d,key) :
    if d.has_key(key) :
        k = d[key]
        del d[key]
        return k
    else :
        return None

def get_or_create_group(name, type=GROUP, **kwargs) :

    if TgGroup.objects.filter(group_name=name).count() > 0 :
        return TgGroup.objects.get(group_name=name)

    create_hosts = extract(kwargs,'create_hosts')
    location = extract(kwargs,'location')
    created = extract(kwargs,'created')
    display_name = extract(kwargs,'display_name')

    if not location :
        location,flag = Location.objects.get_or_create(name='VirtualLocation')

    if not created :
        created = datetime.datetime.today()

    g = TgGroup(group_name=name, place=location, created=created, display_name=display_name, **kwargs)
    g.type = type
    g.save()

    if create_hosts : 
            h = TgGroup(group_name='%s-admin'%name, display_name='%s Admin'%display_name,  place=location, **kwargs) 
            h.type = HOSTS
            h.save()
            # XXX Not currently setting this to be the default host ... does that idea still exist?
    else :
        h = g # if no admin flag, we make the group its own admin
        
    return g,h


def create_hub(name, **kwargs) :
    g,h = get_or_create_group(name, HUB, **kwargs)
    g.add_member(h)
    return g,h

    
def create_site_group(name,  **kwargs) :
    g,h = get_or_create_group(name, GROUP, **kwargs)
    g.add_member(h)
    return g,h

