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

def get_or_create_group(name, **kwargs) :

    if TgGroup.objects.filter(group_name=name).count() > 0 :
        return TgGroup.objects.get(group_name=name), False

    if kwargs.has_key('location') : 
        location = kwargs['location']
    else :
        from apps.hubplus_compatibility.models import Location
        location,created = Location.objects.get_or_create(name='virtual')

    g = TgGroup(group_name=name, place=location, created=datetime.datetime.today(), **kwargs)
    g.save()
    return g, True


def my_create_group(name, type, **kwargs) :
    if 'create_hosts' in kwargs :
        if kwargs['create_hosts'] :
            kw2 = {}
            kw2.update(kwargs)
            del kw2['create_hosts']
            g,created = my_create_group('%s-admin'%name, **kw2) 
            g.type = type
            g.save()
            display_name = kw2['display_name']
            del kw2['display_name']
            h,bb = my_create_group('%s-admin'%name, HOSTS, display_name='%s Admin'%display_name, **kw2) 
            h.save()
    else :
        g,created = my_create_group('%s-admin'%name, HOSTS, **kw2) 
        h = g # if no admin flag, we make the group its own admin
        
    return g,h


def create_hub(name, **kwargs) :
    g,h = my_create_group(name, HUB, **kwargs)
    g.add_member(h)
    return g,h

    
def create_site_group(name,  **kwargs) :
    g,h = my_create_group(name, GROUP, **kwargs)
    g.add_member(h)
    return g,h

