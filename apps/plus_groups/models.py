from django.db import models

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
    

