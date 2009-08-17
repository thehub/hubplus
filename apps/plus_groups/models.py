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



def create_hub(name, **kwargs) :
    g,h = get_or_create_group(name, HUB, **kwargs)
    g.add_member(h)
    return g,h

    
def create_site_group(name,  **kwargs) :
    g,h = get_or_create_group(name, GROUP, **kwargs)
    g.add_member(h)
    return g,h

