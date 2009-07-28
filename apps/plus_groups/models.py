from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User, UserManager, check_password

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.hubspace_compatibility.models import TgGroup

class GroupExtras(models.Model) :
    """ Rather than hack the TgGroup table, we'll add the extras here. 
    To consider : would this be better as a subclass of TgGroup?"""
    
    tg_group = models.OneToOneField(TgGroup, primary_key=True)
    about = models.TextField('about', null=True, blank=True)
    group_type = models.CharField('type',max_length=30)
    

 
def create_group_extras(sender, instance=None, **kwargs) :
    if instance is None : 
        return
    group_extras, created = GroupExtras.objects.get_or_create(tg_group=instance)

post_save.connect(create_group_extras,sender=TgGroup) 


