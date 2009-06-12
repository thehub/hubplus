
from django.db import models

from django.contrib.auth.models import User, UserManager, check_password


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


import hashlib

def getHubspaceUser(username) :
    """ Returns the hubspace user. None if doesn't exist"""
    try :
        tu = User.objects.filter(username=username)[0]
        return  tu
    except Exception,e:
        print "Error in getHubspaceUser %s" % e
        return None


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
def encrypt_password(password) :
    return hashlib.md5(password).hexdigest()

# The following will be patched into the User object in the 
def set_password(self,raw) :
    self.password = encrypt_password(raw)

def check_password(self,raw) :
    return self.password == encrypt_password(raw)

# 
class HubspaceCompatibilityNotToBeSavedException(Exception) : 
    def __init__(self,cls,extra) :
        self.cls = cls
        self.extra = extra

class TgUser(models.Model):
    user_name = models.CharField(unique=True, max_length=255)
    email_address = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=40)

    class Meta:
        db_table = u'tg_user'

    def save(self) :
        raise HubspaceCompatibilityNotToBeSavedException(TgUser,'User_name:%s'%self.user_name)


class HubspaceAuthenticationBackend :
    """
    Authenticate against HubSpace database for user login and 
    """

    def getUserClass(self) : return User
    def createUser(self,username,password,email='') :
        self.getUserClass()(username=username,password=password,email=email)
    def findUser(self,username) :
        return self.getUserClass().objects.filter(username=username)[0]
    def getOrCreateUser(self,username,password='',email='') :
        try :
            u = self.findUser(username)
        except Exception, e:
            try :
                u = self.createUser(username,password,email)
            except Exception, e:
                u = None
        return u


    def authenticate(self, username=None, password=None):
        login_valid = True
        pwd_valid = True

        UserClass = self.getUserClass()

        try:
            hubspaceUser = getHubspaceUser(username)
            if  hubspaceUser == None : 
                print "there is no hubspace user called '%s'" % username
                return None # Doesn't exist in Hubspace database

            print "user password %s :: encrypt %s" % (hubspaceUser.password,encrypt_password(password))
            if not (hubspaceUser.password == encrypt_password(password)) : return None # Password doesn't match
            djangoUser = self.getOrCreateUser(username,hubspaceUser.password)
            self.refresh(hubspaceUser,djangoUser)  # allow subclasses to over-ride the refresh 
            print "got %s" % djangoUser
            return djangoUser
        except Exception, e:
            print 'Error3 %s' % e
            # What went wrong here? Needs handling
            pass
        return None

    def refresh(self,hubspaceUser,djangoUser) :
        #djangoUser.password = hubspaceUser.password
        #djangoUser.save()
        pass

    def get_user(self, user_id):
        UserClass = self.getUserClass()
        try:
            return UserClass.objects.get(pk=user_id)
        except UserClass.DoesNotExist:
            return None

class Location(models.Model):

    name = models.CharField(unique=True, max_length=200)
    class Meta:
        db_table = u'location'

try :
  class TgGroup(models.Model):
    #id = models.IntegerField(primary_key=True)
    group_name = models.CharField(unique=True, max_length=40)
    display_name = models.CharField(max_length=255)
    created = models.DateTimeField()
    place = models.ForeignKey(Location)
    level = models.CharField(max_length=9)

    class Meta:
        db_table = u'tg_group'

    def is_group(self) : return True

    def add_member(self,x) :
        if not self.has_member(x) :
            map = HCGroupMapping()
            map.child=x
            map.parent=self
            map.save()


    def remove_member(self,x) :
        for map in HCGroupMapping.objects.filter(parent=self) :
            if map.child == x :
                map.delete()
        
    def get_members(self) : 
        return (x.child for x in HCGroupMapping.objects.filter(parent=self))

    def has_member(self,x) :
        return (x in self.get_members())

    def get_no_members(self) :
        return HCGroupMapping.objects.filter(parent=self).count()

    def __str__(self) : return "<TgGroup : %s>" % self.group_name

  class HCGroupMapping(models.Model) :
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    child = generic.GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey(TgGroup)

except Exception, e:
  print "##### %s" % e

# We're going to add the following method to User class
def is_member_of(self,group) : 
    if not group.is_group() : return False
    if group.has_member(self) : return True
    # not a direct member, but perhaps somewhere up the tree of (enclosures / parents)
    for x in self.get_enclosures() :
        if x.is_member_of(group) : 
            return True
    return False
    
# add it to TgGroup too
TgGroup.is_member_of= is_member_of

# to be added to User class
def get_enclosures(self) :
    return (x.parent for x in HCGroupMapping.objects.all() if x.child == self)

TgGroup.get_enclosures = get_enclosures

# to be added to User class
def is_direct_member_of(self, group) :
    return group.has_member(self)

TgGroup.is_direct_member_of = is_direct_member_of

