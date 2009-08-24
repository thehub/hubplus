from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from apps.plus_permissions.default_agents import get_admin_user, get_site

from timezones.fields import TimeZoneField

import itertools

class DelegateToUser(object) :
   def __init__(self,attr_name) : self.attr_name = attr_name
   def __get__(self,obj,typ=None) : return getattr(obj.user,self.attr_name)
   def __set__(self,obj,val) : 
       #print "setting %s to %s for %s (class %s (user = %s, cls = %s))" % (self.attr_name,val,obj,obj.__class__,obj.user, obj.user.__class__)
       setattr(obj.user,self.attr_name,val)
       #print "Getting from inner %s" % getattr(obj.user,self.attr_name)

class Profile(models.Model):    
   user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
   
   about = DelegateToUser('description')
   email_address = DelegateToUser('email_address')
   name = DelegateToUser('username')
   display_name = DelegateToUser('display_name')
   first_name = DelegateToUser('first_name')
   last_name = DelegateToUser('last_name')
   organisation = DelegateToUser('organisation')
   role = DelegateToUser('title')
   mobile = DelegateToUser('mobile')
   home = DelegateToUser('home')
   work = DelegateToUser('work')
   fax = DelegateToUser('fax')
   
   email2 = DelegateToUser('email2')
   address = DelegateToUser('address')
   skype_id = DelegateToUser('skype_id')
   sip_id = DelegateToUser('sip_id')
   website = DelegateToUser('website')
   homeplace = DelegateToUser('homeplace')
   location = DelegateToUser('location')
   
   invited_by = models.ForeignKey(User, related_name='invited_users', null=True)
   accepted_by = models.ForeignKey(User, related_name='accepted_users', null=True)

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


   class Meta:
      verbose_name = _('profile')
      verbose_name_plural = _('profiles')

import logging


def create_profile(sender, instance=None, **kwargs):
   if instance is None:
      return

   # The admin user can't have a profile created automatically like this 
   if instance.username == 'admin' : 
      return
   import ipdb
   #ipdb.set_trace()
   
   god = get_admin_user()
   site = get_site(god)
   if Profile.objects.filter(user__username=instance.username).count() < 1 :
      profile = site.create_Profile(instance, user=instance)

post_save.connect(create_profile, sender=User)

class HostInfo(models.Model):
    """ Information asked by hosts about this user """
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
   
    find_out = models.TextField(_('find_out'), null=True, blank=True)
    peer_mentoring = models.BooleanField()
    project = models.TextField(_('project'),max_length=250, null=True,blank=True)
    project_stage = models.TextField(max_length=250,null=True,blank=True)
    assistance_offered = models.TextField(max_length=250,null=True,blank=True)



 
def create_host_info(sender, instance=None, **kwargs) :
    if instance is None : 
        return
    host_info, created = HostInfo.objects.get_or_create(user=instance)

post_save.connect(create_host_info,sender=User) 

