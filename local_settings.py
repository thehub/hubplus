from django.contrib.auth.models import User
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

    User.user_name = AliasOf('username')
    User.email = AliasOf('email_address')
    User._meta.db_table = 'tg_user'
    User.set_password = set_password
    User.check_password = check_password
    User.isMemberOf = isMemberOf
    User.isDirectMemberOf = isDirectMemberOf
    User.getEnclosures = getEnclosures

    
    print "Monkey Patched User Class ... gulp!"
    # Finished the User Patch
