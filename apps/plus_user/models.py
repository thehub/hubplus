from django.db import models
import datetime
from django.contrib.auth.models import User, UserManager, AnonymousUser, check_password
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save
import hashlib
import datetime
from apps.plus_groups.models import is_member_of,  is_direct_member_of,  get_enclosures, get_enclosure_set, Location

"""TODO:
1. Bring in Location Data for Hub - define Hub as the Hub's members group object with an associated Location
2. Implement the hubspace metadata framework - add typed metadata and language along the way
3. Implement the Hub Microsites list functionality
"""

class AliasOf(object):
   def __init__(self,name): 
       self.name = name

   def __get__(self,obj,typ=None): 
       return getattr(obj,self.name)

   def __set__(self,obj,val): 
       setattr(obj,self.name,val)


def user_save(self) :
    if not self.created :
        self.created = datetime.date.today()
    super(User,self).save()
    

def to_db_encoding(s, encoding):
    if isinstance(s, str):
        pass
    elif hasattr(s, '__unicode__'):
        s = unicode(s)
    if isinstance(s, unicode):
        s = s.encode(encoding)
    return s

# __________

class UserNameField(models.CharField) :
    """ Django works with a User class. Our system, for Hubspace compatibility reasons, needs to use a tg_user table.
    We will also use this table, but need to cope with the fact that we will have a user_name and a username field
    Whenever we update user_name we want to also update username.
    And whenever we update username we want to also update user_name.
    This class helps us"""
    
    def pre_save(self,model_instance,add) :
        model_instance.user_name = model_instance.username
        return getattr(model_instance, self.attname)

    def __setattr__(self,obj,val) :
        print "In __setattr__ %s, %s" % (obj,val)
        super(models.CharField,self).__setattr__(obj,val)


# ______
from hashlib import sha1
import hmac as create_hmac

def psn_encrypt(hmac_key, password):
    """bizarely we use a field containing the fullname of the user as an hmac key for the hash of passwords from Plone
    """
    return create_hmac.new(str(hmac_key), password, sha1).hexdigest()


def encrypt_password(password):
   """We need to change this to start using SHA1 or higher for new passwords
   """
   return hashlib.md5(password).hexdigest()

# The following will be patched into the User object in hubspace_compatibility.py

def set_password(self, raw):
    self.password = encrypt_password(raw)

def check_password(self, raw):
    if self.password.startswith('hmac_sha'):
        return self.password.split('hmac_sha:')[1] == psn_encrypt(self.psn_password_hmac_key, raw)
    else:
        return self.password == encrypt_password(raw)
    

class HubspaceCompatibilityNotToBeSavedException(Exception) : 
    def __init__(self,cls,extra) :
        self.cls = cls
        self.extra = extra


class HubspaceAuthenticationBackend :
    """
    Authenticate against HubSpace database for user login and 
    """

    def authenticate(self, username=None, password=None):
        login_valid = True
        pwd_valid = True

        try:
            if User.objects.filter(username=username).count() < 1 :
                return None # Doesn't exist in Hubspace database

            user = User.objects.get(username=username)
            if user.check_password(password):
               return user
            return None

        except Exception, e:
            print 'Error3 %s' % e
            # What went wrong here? Needs handling
            pass
        return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None



def patch_user_class():    
    User._meta.db_table = 'tg_user'

    # Patching the User class

    User.add_to_class('user_name', UserNameField(unique=True, max_length=255))
    User.add_to_class('email_address', models.CharField(max_length=255,unique=True))
    del User.groups
    #User.add_to_class('active',models.SmallIntegerField(null=True)) # not shown
    #User.add_to_class('display_name', models.CharField(max_length=255,null=True))

    User.add_to_class('description', models.TextField())
    User.add_to_class('organisation', models.CharField(max_length=255)) 
    User.add_to_class('title', models.CharField(max_length=255,null=True))
    User.add_to_class('mobile', models.CharField(max_length=30))
    User.add_to_class('work', models.CharField(max_length=30))
    User.add_to_class('home', models.CharField(max_length=30))
    User.add_to_class('fax', models.CharField(max_length=30))
    User.add_to_class('place', models.CharField(max_length=150, null=True))

    User.add_to_class('created',models.DateTimeField(default=datetime.datetime.now))
    User.add_to_class('email2',models.CharField(max_length=255))
    User.add_to_class('email3',models.CharField(max_length=255))
    User.add_to_class('address',models.TextField())
    User.add_to_class('skype_id',models.TextField())
    User.add_to_class('sip_id',models.TextField())
    User.add_to_class('website',models.TextField())
    User.add_to_class('homeplace', models.ForeignKey(Location, null=True))

    User.add_to_class('psn_id', models.CharField(max_length=50,null=True))
    User.add_to_class('psn_password_hmac_key', models.CharField(max_length=50, null=True)) #this is just for the bizare hmacing of psn passwords by a field formly known as "fullname"
    
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
