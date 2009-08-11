
from django.db import models

from django.contrib.auth.models import User, UserManager, check_password

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save

import hashlib
import datetime

"""TODO:
1. Respect hubspace memberships
i)  define user_group many-to-many
ii) define group is member_of group as a many-to-many
iii) deprecate HC
iv) Implement is_user_of()
v) "is_member_of", "get_enclosures", "is direct member of" should check for "is_user_of"

2.. Bring in Location Data for Hub
3. Define Hub as the Hub's members group object with an associated Location
6. Where is group's extra?? why not just extend
7. Implement the hubspace metadata framework - add typed metadata and language along the way
8. Implement the Hub Microsites list functionality
"""

def getHubspaceUser(username) :
    """ Returns the hubspace user. None if doesn't exist"""
    try :
        tu = User.objects.get(username=username)
        return  tu
    except Exception,e:
        print "Error in getHubspaceUser %s" % e
        return None


class UserGroup(models.Model):
    group_id = models.IntegerField()
    user_id = models.IntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'user_group'



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

# The following will be patched into the User object in the  --- WHERE! Tom
def set_password(self,raw) :
    self.password = encrypt_password(raw)

def check_password(self,raw) :
    return self.password == encrypt_password(raw)

# 
class HubspaceCompatibilityNotToBeSavedException(Exception) : 
    def __init__(self,cls,extra) :
        self.cls = cls
        self.extra = extra


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
    group_name = models.CharField(unique=True, max_length=40)
    display_name = models.CharField(max_length=255)
    created = models.DateTimeField()
    place = models.ForeignKey(Location)
    #if place is Hub Islington then set member of toHub Islington group if level is member
    #if level is host, set member of to Hub Islington Host Group.
    level = models.CharField(max_length=9)
    psn_id = models.CharField(max_length=100)
    path = models.CharField(max_length=120)

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


    def get_permission_agent_name(self) : 
        return self.display_name


    def get_extras(self) :
        # if there are extras for this class, return them
        return self.groupextras

    def get_default_admin(self) :
        from apps.plus_permissions.models import default_admin_for
        return default_admin_for(self)
        
    def __str__(self) : return "<TgGroup : %s>" % self.group_name

  class HCGroupMapping(models.Model) :
      """XXX Effectively this is a many-to-many relationship between a group and its members.
      I guess it is explicit because of the need for a GenericForeignKey to reference User and Group tables for the child.
      I find this unnecessary and undesirable because:
      a) we already have a user_group relation in hubspace 
      b) it might sometimes be useful to distinguish group memberships from user membership relations
      Therfore I will add a many-to-many relation for groups called is_parent_of. And user the existing user_group relation from hubspace. This will also enhance hubspace's access to HubPlus defined groups.
      This relationship should then be deprecated.
      """
      content_type = models.ForeignKey(ContentType)
      object_id = models.PositiveIntegerField()
      child = generic.GenericForeignKey('content_type', 'object_id')
      parent = models.ForeignKey(TgGroup)

except Exception, e:
  print "##### %s" % e

# We're going to add the following method to User class (and to group)
def is_member_of(self,group) : 
    if not group.is_group() : return False
    if group.has_member(self) : return True
    # not a direct member, but perhaps somewhere up the tree of (enclosures / parents)
    for x in self.get_enclosures() :
        if x.is_member_of(group) : 
            return True
    return False
    
# add it to TgGroup too
TgGroup.is_member_of = is_member_of

# to be added to User class
def get_enclosures(self) :
    """Give us all the things of which this user is a member_of
    XXX parent should not be called "parent", it is the current node
    XXX implement in SQL it is not so hard I think
    """
    return (x.parent for x in HCGroupMapping.objects.all() if x.child == self)

TgGroup.get_enclosures = get_enclosures

# set of all enclosures
# to be added to User class


def get_enclosure_set(self) :
    es = set([self])
    for e in self.get_enclosures() :
        if e != self :
            es = es.union(e.get_enclosure_set())
    return es
    

TgGroup.get_enclosure_set = get_enclosure_set

# to be added to User class
def is_direct_member_of(self, group) :
    return group.has_member(self)

TgGroup.is_direct_member_of = is_direct_member_of

# to be added to User class
def get_permission_agent_name(self) :
    return self.username

# to be added to user class
def corresponding_agent(self) :
    agent_type = ContentType.objects.get_for_model(self)
    return Agent.objects.get(agent_content_type=agent_type,agent_object_id=self.id)

TgGroup.corresponding_agent = corresponding_agent

def user_save(self) :
    if not self.created :
        self.created = datetime.date.today()
    super(User,self).save()
    


# Agents are used by plus_permissions.SecurityTag to make a many-to-many relationship with agents such as 
# Users and TgGroups

class Agent(models.Model) :
    agent_content_type = models.ForeignKey(ContentType,related_name='security_tag_agent')
    agent_object_id = models.PositiveIntegerField()
    agent = generic.GenericForeignKey('agent_content_type', 'agent_object_id')

    def get_type_and_id(self) :
        return ContentType.objects.get_for_model(self), self.id


def create_agent(sender, instance=None, **kwargs):
    if instance is None:
        return
    instance_type = ContentType.objects.get_for_model(instance)
    agent, created = Agent.objects.get_or_create(agent_content_type=instance_type,agent_object_id=instance.id)
    agent.save()

post_save.connect(create_agent, sender=User)
post_save.connect(create_agent, sender=TgGroup)



# ======================================
# The hubspace object reference model

class ObjectReference(models.Model):
    """ Generic object reference, based on version in Hubspace"""
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')


def make_object_reference(object) :
    if not object.pk : 
        object.save()
    o = ObjectReference(object=object)
    o.save()
    return o

def get_referenced_object(id) :
    return ObjectReference.objects.get(pk=id).object
