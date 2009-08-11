from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User, UserManager, check_password

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.hubspace_compatibility.models import TgGroup

from apps.plus_permissions.models import DefaultAdmin

import datetime

class GroupExtras(models.Model) :
    """ Rather than hack the TgGroup table, we'll add the extras here. 
    To consider : would this be better as a subclass of TgGroup?"""
    
    tg_group = models.OneToOneField(TgGroup, primary_key=True)
    about = models.TextField('about', null=True, blank=True)
    group_type = models.CharField('type',max_length=30)
    
    psn_id = models.CharField(max_length=120)
    path = models.CharField(max_length=120)

    title = models.CharField(max_length=60)
    description = models.TextField()

    body = models.TextField()
    rights = models.TextField()

 
def create_group_extras(sender, instance=None, **kwargs) :
    if instance is None : 
        return
    group_extras, created = GroupExtras.objects.get_or_create(tg_group=instance)

post_save.connect(create_group_extras,sender=TgGroup) 


# Group types
HUB     = 'HUB'
GROUP   = 'GROUP'
MEMBERS = 'MEMBERS'
HOSTS   = 'HOSTS'

def my_create_group(name, display_name, type, *argv, **kwargs) :

    g = TgGroup(group_name=name, display_name=display_name, place=None, created=datetime.datetime.today())
    g.save()
    e = g.get_extras()
    e.group_type = type
    e.save()


    if 'create_hosts' in kwargs :
        if kwargs['create_hosts'] :
            kw2 = {}
            kw2.update(kwargs)
            del kw2['create_hosts']
            h,bb = my_create_group('%s-admin'%name, '%s Admin'%display_name, HOSTS, *argv, **kw2) 
            h.save()
    
    else :
        h = g # if no admin flag, we make the group its own admin
        
    da = DefaultAdmin(agent=h,resource=g)
    da.save()

    return g,h

def create_hub(name, display_name,  *argv, **kwargs) :
    g,h = my_create_group(name, display_name, HUB, *argv, **kwargs)
    g.add_member(h)
    return g,h

    
def create_site_group(name, display_name, *argv, **kwargs) :
    g,h = my_create_group(name, display_name, GROUP, *argv, **kwargs)
    g.add_member(h)
    return g,h

