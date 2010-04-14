from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from apps.plus_permissions.default_agents import get_admin_user, get_site

from timezones.fields import TimeZoneField
from datetime import datetime

import itertools

class DelegateToUser(object) :
   def __init__(self,attr_name) : self.attr_name = attr_name
   def __get__(self,obj,typ=None) : return getattr(obj.user,self.attr_name)
   def __set__(self,obj,val) : 
       #print "setting %s to %s for %s (class %s (user = %s, cls = %s))" % (self.attr_name,val,obj,obj.__class__,obj.user, obj.user.__class__)
       setattr(obj.user,self.attr_name,val)
       #print "Getting from inner %s" % getattr(obj.user,self.attr_name)

class ProfileStatusDescriptor(object):
    # XXXX Bah! There has to be a better way than this, but
    # because we're using the Profile, we have to get the user 

    def __get__(self,profile,typ=None):
        from apps.microblogging.models import TweetInstance
        return TweetInstance.objects.tweets_from(profile.user).order_by("-sent")[0].text

    def __set__(self,profile,val):
        from apps.microblogging.models import send_tweet
        send_tweet(profile.user,val)


class Profile(models.Model):    
   user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
   def content(self):
      return """
%s
%s""" % (self.get_display_name(), self.about)
   about = DelegateToUser('description')
   email_address = DelegateToUser('email_address')
   name = DelegateToUser('username')
   display_name = DelegateToUser('display_name')
   active = DelegateToUser('active')
   first_name = DelegateToUser('first_name')
   last_name = DelegateToUser('last_name')
   organisation = DelegateToUser('organisation')
   role = DelegateToUser('title')
   mobile = DelegateToUser('mobile')
   home = DelegateToUser('home')
   work = DelegateToUser('work')
   fax = DelegateToUser('fax')
   post_or_zip = DelegateToUser('post_or_zip')   
   country = DelegateToUser('country')
   email2 = DelegateToUser('email2')
   address = DelegateToUser('address')
   skype_id = DelegateToUser('skype_id')
   sip_id = DelegateToUser('sip_id')
   website = DelegateToUser('website')
   homeplace = DelegateToUser('homeplace')
   homehub = DelegateToUser('homehub')

   place = DelegateToUser('place')
   
   invited_by = models.ForeignKey(User, related_name='invited_users', null=True)
   accepted_by = models.ForeignKey(User, related_name='accepted_users', null=True)

   status = ProfileStatusDescriptor()

   

   def __unicode__(self):
       return self.user.username

   def __str__(self) :
      return "this is a profile for %s" % self.user.username

   def was_invited(self):
      return not self.invited_by is None

   def was_accepted(self):
      return not self.accepted_by is None
    
   def get_absolute_url(self):
      return ('profile_detail', None, {'username': self.user.username})

   get_absolute_url = models.permalink(get_absolute_url)
    
   def has_somethings(self,f) :
      try :
         first = f().next()
      except StopIteration :
         return False
      else :
         return True

   def has_something(self,fun,match) :
      return (match.label in (x.label for x in fun()))
   

   def get_host_info(self) :
      hi, created = HostInfo.objects.get_or_create(user=self.user)
      if created :
         hi.save()
      return hi

   def save(self):
      super(Profile, self).save()
      ref = self.get_ref()
      ref.modified = datetime.now()
      ref.display_name = self.get_display_name()
      ref.save()


   class Meta:
      verbose_name = _('profile')
      verbose_name_plural = _('profiles')

import logging


class HostInfo(models.Model):
    """ Information asked by hosts about this user """
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
   
    find_out = models.TextField(_('find_out'), null=True, blank=True)
    peer_mentoring = models.BooleanField() 
    expected_membership_benefits = models.TextField(max_length=250, null=True, blank=True)   
    project = models.TextField(_('project'),max_length=250, null=True, blank=True)
    project_stage = models.TextField(max_length=250,null=True, blank=True)
    assistance_offered = models.TextField(max_length=250,null=True, blank=True)

 
def create_host_info(sender, instance=None, **kwargs) :
    if instance is None : 
        return
    if HostInfo.objects.filter(user__username=instance.username).count() < 1  :
       profile = instance.create_HostInfo(instance, user=instance)

def create_profile(sender, instance=None, **kwargs):
   if instance is None:
      return
   if Profile.objects.filter(user__username=instance.username).count() < 1 :
      profile = instance.create_Profile(instance, user=instance)


