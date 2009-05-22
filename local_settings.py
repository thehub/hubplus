from django.contrib.auth.models import User

class AliasOf(object) :
   def __init__(self,true) : self.true = true
   def __get__(self,obj,typ=None) : return getattr(obj,self.true)
   def __set__(self,obj,val) : setattr(obj,self.true,val)

try :
    if hub_local_settings : pass
except :
    # do it once
    hub_local_settings = True

    # Patching the User class

    User.user_name = AliasOf('username')
    User.email = AliasOf('email_address')
    User._meta.db_table = 'tg_user'


    
    print "Monkey Patched User Class ... gulp!"
    # Finished the User Patch

    
