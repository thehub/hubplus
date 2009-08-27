from django.contrib.auth.models import User, AnonymousUser, UserManager
from django.db import models


import datetime

try :
    from apps.hubspace_compatibility.models import *
except Exception, e:
    print "ABC"
    print e




try :
    if hub_local_settings : pass
except :
    # do it once
    hub_local_settings = True
    
    User._meta.db_table = 'tg_user'

    # Patching the User class

    User.add_to_class('user_name', UserNameField(unique=True, max_length=255))
    User.add_to_class('email_address', models.CharField(max_length=255,unique=True))
    del User.groups
    #User.add_to_class('active',models.SmallIntegerField(null=True)) # not shown
    User.add_to_class('display_name', models.CharField(max_length=255,null=True))

    User.add_to_class('description', models.TextField())
    User.add_to_class('organisation', models.CharField(max_length=255)) 
    User.add_to_class('title', models.CharField(max_length=255,null=True))
    User.add_to_class('mobile', models.CharField(max_length=30))
    User.add_to_class('work', models.CharField(max_length=30))
    User.add_to_class('home', models.CharField(max_length=30))
    User.add_to_class('fax', models.CharField(max_length=30))
    User.add_to_class('place', models.CharField(max_length=50, null=True))

    User.add_to_class('created',models.DateTimeField(default=datetime.datetime.now))
    User.add_to_class('email2',models.CharField(max_length=255))
    User.add_to_class('email3',models.CharField(max_length=255))
    User.add_to_class('address',models.TextField())
    User.add_to_class('skype_id',models.TextField())
    User.add_to_class('sip_id',models.TextField())
    User.add_to_class('website',models.TextField())
    User.add_to_class('homeplace',models.ForeignKey(Location,null=True))
    
    User.email = AliasOf('email_address')
    User.set_password = set_password
    User.check_password = check_password
    User.is_member_of = is_member_of
    User.is_direct_member_of = is_direct_member_of
    User.get_enclosures = get_enclosures
    User.get_enclosure_set = get_enclosure_set
    User.is_group = lambda(self) : False
    User.save = user_save
   
    print "Monkey Patched User Class ... gulp!"

    AnonymousUser.is_member_of = lambda *args, **kwargs : False
    AnonymousUser.is_direct_member_of = lambda *args, **kwarg : False
    # Finished the User Patch
