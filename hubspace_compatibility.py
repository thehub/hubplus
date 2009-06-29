from django.contrib.auth.models import User,UserManager
from django.db import models

import datetime

try :
    from apps.hubspace_compatibility.models import *
except Exception, e:
    print e

class AliasOf(object) :
   def __init__(self,true) : self.true = true
   def __get__(self,obj,typ=None) : return getattr(obj,self.true)
   def __set__(self,obj,val) : setattr(obj,self.true,val)


try :
    if hub_local_settings : pass
except :
    # do it once
    hub_local_settings = True
    print "**************"
    
    
    # Patching the User class

    User.add_to_class('user_name',UserNameField(unique=True, max_length=255))
    User.add_to_class('email_address',models.CharField(max_length=20))

    #User.add_to_class('active',models.SmallIntegerField(null=True)) # not shown
    User.add_to_class('display_name',models.CharField(max_length=255,null=True))
    User.add_to_class('title',models.CharField(max_length=255,null=True))
    User.add_to_class('mobile',models.CharField(max_length=30))
    User.add_to_class('work',models.CharField(max_length=30))

    User.add_to_class('home',models.CharField(max_length=30))
    User.add_to_class('fax',models.CharField(max_length=30))

    User.add_to_class('created',models.DateTimeField())
    User.add_to_class('email2',models.CharField(max_length=255))
    User.add_to_class('email3',models.CharField(max_length=255))
    User.add_to_class('address',models.TextField())
    User.add_to_class('skype_id',models.TextField())
    User.add_to_class('sip_id',models.TextField())
    User.add_to_class('website',models.TextField())
    User.add_to_class('homeplace',models.ForeignKey(Location,null=True))
    
    User.email = AliasOf('email_address')
    User._meta.db_table = 'tg_user'
    User.set_password = set_password
    User.check_password = check_password
    User.is_member_of = is_member_of
    User.is_direct_member_of = is_direct_member_of
    User.get_enclosures = get_enclosures
    User.is_group = lambda(self) : False
    User.save = user_save
   
    print "Monkey Patched User Class ... gulp!"
    # Finished the User Patch
