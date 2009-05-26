
from django.db import models

from django.contrib.auth.models import User, UserManager, check_password
import hashlib

def getHubspaceUser(username) :
    """ Returns the hubspace user. None if doesn't exist"""
    try :
        tu = User.objects.filter(username=username)[0]
        print "got %s, %s" % (tu.username,tu.password)
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
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=200)
    class Meta:
        db_table = u'location'

try :
  class TgGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    group_name = models.CharField(unique=True, max_length=40)
    display_name = models.CharField(max_length=255)
    created = models.DateTimeField()
    place = models.ForeignKey(Location)
    level = models.CharField(max_length=9)

    enclosures = models.ManyToManyField("self")
    members = models.ManyToManyField("self")

    class Meta:
        db_table = u'tg_group'
except  Exception, e :
  print "#### %s" % e

