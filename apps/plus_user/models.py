from django.db import models
import settings
import datetime
from django.contrib.auth.models import User, UserManager, AnonymousUser, check_password
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save
import hashlib
import datetime
from apps.plus_groups.models import is_member_of,  is_direct_member_of,  get_enclosures, get_enclosure_set, Location

from django.conf import settings 
from django.template import Template, Context


"""TODO:
1. Bring in Location Data for Hub
2. add typed metadata and language along the way
3. Implement the Hub Microsites list functionality
"""

class AliasOf(object):
   def __init__(self, name): 
       self.name = name

   def __get__(self, obj, typ=None): 
       return getattr(obj, self.name)

   def __set__(self, obj, val): 
       setattr(obj, self.name, val)


def user_save(self) :
    if not self.created :
        self.created = datetime.date.today()

    if self.homehub and (self.homeplace != self.homehub.place) :
       self.homeplace = self.homehub.place

    super(User,self).save()
    self.post_save()

def post_save(self) :
    # profile
    try:
       ref = self.get_profile().get_ref()
    except :
       # profile not created yet
       return

    # 
    ref.modified = datetime.datetime.now()
    ref.display_name = self.get_display_name()
    ref.save()

    

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


def get_meta_data(obj, attr):
   try:
      return UserMetaData.objects.filter(user=obj.__dict__['id'], attr_name=attr)[0]
   except IndexError:
      return None


def __getattr__(self, attr):
   """Only called if normal attribute lookup fails
   """
   if attr.startswith('md_'):
      return get_meta_data(self, attr[3:]).attr_value

   try:
      return self.__dict__[attr]
   except:
      raise AttributeError
   
      #except KeyError:
      #   if attr in type(self).__dict__ and hasattr(type(self).__dict__[attr], '__get__'):
      #   #instance descriptor e.g. AliasOf
      #      type(self).__dict__[attr].__get__(self, type(self))
    #try:
    #   return self.__dict__[attr]
    #except KeyError:
    #   return get_meta_data(self, attr).attr_value

def __setattr__(self, attr_name, attr_value):
   if attr_name.startswith('md_'):
      meta_data = get_meta_data(self, attr_name[3:])
      if meta_data:
         meta_data.attr_value = attr_value
         meta_data.save()
      else:
         u_md = UserMetaData(user=self, attr_name=attr_name[3:], attr_value=attr_value)
         u_md.save()

   else:
       models.Model.__setattr__(self, attr_name, attr_value)



    #if attr_name in self._meta.get_all_field_names() or \
    #       attr_name.endswith('_id') and attr_name[:-3] in self._meta.get_all_field_names() or \
    #       attr_name.endswith('_cache') and attr_name[1:-6] in self._meta.get_all_field_names():
    #   self.__dict__[attr_name] = attr_value
    #elif attr_name in type(self).__dict__ and hasattr(type(self).__dict__[attr_name], '__set__'):
    #   #instance descriptor e.g. AliasOf
    #   type(self).__dict__[attr_name].__set__(self, attr_value)
    #else:
    #   meta_data = get_meta_data(self, attr_name)
    #   if meta_data:
    #      meta_data.attr_value = attr_value
    #      meta_data.save()
    #   else:
    #      UserMetaData(user=self, attr_name=attr_name, attr_value=attr_value)
          



def patch_user_class():
    """access biz_type, introduced_by and postcode through prefixing 'md_' e.g user.md_biz_type.
    """
    from apps.plus_groups.models import TgGroup, User_Group  
    User._meta.db_table = 'tg_user'
    # Patching the User class
    User.add_to_class('__getattr__',  __getattr__)
    User.add_to_class('__setattr__',  __setattr__)

    # EXPERIMENT ... make username alias of user_name
    User.add_to_class('user_name', UserNameField(unique=True, max_length=255))
    #User.add_to_class('user_name',models.CharField(max_length=255,unique=True))
    #del User.username
    #User.add_to_class('username',AliasOf('user_name'))                      
    # EXPERIMENT END

    User.add_to_class('email_address', models.CharField(max_length=255,unique=True))

    #remove the existing django groups relation  
    gr = User._meta.get_field('groups')
    User._meta.local_many_to_many.remove(gr)
    del User.groups
    # add ours new relation for groups
    User.add_to_class('groups', models.ManyToManyField(TgGroup, through=User_Group, related_name='users'))

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
    User.add_to_class('skype_id',models.TextField())
    User.add_to_class('sip_id',models.TextField())
    User.add_to_class('website',models.TextField())
    User.add_to_class('homeplace', models.ForeignKey(Location, null=True))
    User.add_to_class('address', models.TextField())
    User.add_to_class('country', models.CharField(null=True, default="", max_length=2))

    User.add_to_class('homehub', models.ForeignKey("plus_groups.TgGroup", null=True)) # we need this for PSN, XXX need to decide how to make it compatible with hubspace for hub+ 

    User.add_to_class('psn_id', models.CharField(max_length=50,null=True))
    User.add_to_class('psn_password_hmac_key', models.CharField(max_length=50, null=True)) #this is just for the bizare hmacing of psn passwords by a field formly known as "fullname"

    User.add_to_class('cc_messages_to_email',models.BooleanField(default=False)) # internal messages get reflected to email

    User.email = AliasOf('email_address')
    if settings.PROJECT_THEME == 'plus':
       User.post_or_zip = AliasOf('md_postcode')
       User.add_to_class('public_field', models.SmallIntegerField(null=True)) # this will be phased out as it is redundant with the new permissions system
    else:
       User.add_to_class('post_or_zip', models.CharField(null=True, default="", max_length=30))
    
    User.is_active = AliasOf('active') # This takes precedence over the existing is_active field in django.contrib.auth.models
    User.add_to_class('active', models.SmallIntegerField(null=True)) # not currently shown, however setting this to 0 will stop the user logging in

    User.set_password = set_password
    User.check_password = check_password
    User.is_member_of = is_member_of
    User.is_direct_member_of = is_direct_member_of
    User.get_enclosures = get_enclosures
    User.get_enclosure_set = get_enclosure_set
    User.is_group = lambda(self) : False

    User.save = user_save
    User.post_save = post_save

    User.is_admin_of = lambda self, group : self.is_member_of(group.get_admin_group())

    def is_site_admin(self) :
       from apps.plus_permissions.default_agents import get_all_members_group
       return self.is_admin_of(get_all_members_group())
    User.is_site_admin = is_site_admin

    def send_tweet(self, msg) :
       from apps.microblogging.models import send_tweet
       return send_tweet(self, msg)
    User.send_tweet = send_tweet

    def message(self, sender, subject, body) :
       from messages.models import Message
       from django.core.mail import send_mail
       from django.core.urlresolvers import reverse
       from django.utils.translation import ugettext_lazy as _, ugettext

       m = Message(subject=subject, body=body, sender = self, recipient=self)
       m.save()

       if self.cc_messages_to_email :
          # recipient wants emails cc-ed 
          link = 'http://' + settings.DOMAIN_NAME + reverse('messages_all')
          main = _(""" 
%(sender)s has sent you a new message on %(account_name)s .

%(body)s

Click %(link)s to see your account

""") % {'account_name':settings.SITE_NAME, 'body':body, 'link':link, 'sender':sender.get_display_name()}

          self.email_user(subject, main, settings.SUPPORT_EMAIL)

       return m

    User.message = message


    def group_invite_message(self, group, invited_by, accept_url, special_message='') :

       self.message(invited_by, 
                    Template(settings.GROUP_INVITE_SUBJECT_TEMPLATE).render(
             Context({'group_name':group.get_display_name() })),
                    Template(settings.GROUP_INVITE_TEMPLATE).render(
             Context({
                   'first_name':self.first_name,
                   'last_name':self.last_name,
                   'sponsor':invited_by.get_display_name(),
                   'group_name':group.get_display_name(),
                   'site_name':settings.SITE_NAME,
                   'special_message':special_message,
                   'signup_link':accept_url,
                   })
             )+"""
%s""" % accept_url
                    )
    
    User.group_invite_message = group_invite_message


    User.hubs = lambda self : self.groups.filter(group_type=settings.GROUP_HUB_TYPE,level='member')

    User.change_avatar = lambda self : True


    AnonymousUser.is_member_of = lambda *args, **kwargs : False
    AnonymousUser.is_direct_member_of = lambda *args, **kwarg : False

    # Finished the User Patch
    
    



#added from hubspace
class UserMetaData(models.Model):
    """Works the same as Selection above, but for storing free-text properties
    """
    class Meta:
       db_table = 'user_meta_data'    
    user = models.ForeignKey(User, null=True)
    attr_name = models.CharField(max_length=50)
    attr_value = models.TextField()


class Selection(models.Model):
    class Meta:
       db_table = 'selection'
    user = models.ForeignKey(User, null=True)
    attr_name = models.CharField(max_length=50)
    attr_value = models.IntegerField(default=None)
