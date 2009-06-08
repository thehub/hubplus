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

    User.email = AliasOf('email_address')
    User._meta.db_table = 'tg_user'
    User.set_password = set_password
    User.check_password = check_password
    User.is_member_of = is_member_of
    User.is_direct_member_of = is_direct_member_of
    User.get_enclosures = get_enclosures
    User.is_group = lambda(self) : False

    # Over-ride the UserManager's create_user method
    def our_create_user(self,username,email,password=None) :
        """Creates and saves a User with the given username, e-mail and password.

        Directly adapted from Django contrib.auth.models.UserManager.create_user 
        """
        now = datetime.datetime.now()

        user = self.model(None, username, '', '', email.strip().lower(), 'placeholder', False, True, False, now, now)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    UserManager.create_user = our_create_user
    
    print "Monkey Patched User Class ... gulp!"
    # Finished the User Patch
