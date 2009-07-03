from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from timezones.fields import TimeZoneField

import itertools

def get_or_create_something(M,txt) :
    try :
        return M.objects.get(label=txt),False
    except :
        x = M(label=txt)
        x.save()
        return x,True

def get_or_create_interest(txt) :
    return get_or_create_something(InterestTag,txt)

def get_or_create_need(txt) :
    return get_or_create_something(NeedTag,txt)

def get_or_create_skill(txt):
    return get_or_create_something(SkillTag,txt)

class DelegateToUser(object) :
   def __init__(self,attr_name) : self.attr_name = attr_name
   def __get__(self,obj,typ=None) : 
       return getattr(obj.user,self.attr_name)
   def __set__(self,obj,val) : 
       setattr(obj.user,self.attr_name,val)
       obj.user.save()



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

    def __unicode__(self):
        return self.user.username
    
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


    # interests
    def has_interests(self) :
        return self.has_somethings(self.get_interests)

    def get_interests(self) :
        return (x.interest for x in ProfileInterest.objects.filter(user=self.user))

    def has_interest(self,tag) :
        return self.has_something(self.get_interests,tag)

    def add_interest(self,interest_tag) :
        if not self.has_interest(interest_tag) :
            pi = ProfileInterest(interest=interest_tag,user=self.user)
            pi.save()
        

    # needs
    def has_needs(self) :
        return self.has_somethings(self.get_needs)

    def get_needs(self) :
        return (x.need for x in ProfileNeed.objects.filter(user=self.user))

    def has_need(self,tag) :
        return self.has_something(self.get_needs,tag)

    def add_need(self,need_tag) :
        if not self.has_need(need_tag) :
            pn = ProfileNeed(need=need_tag,user=self.user)
            pn.save()


    # skills
    def has_skills(self) :
        return self.has_somethings(self.get_skills)

    def get_skills(self) :
        return (x. skill for x in ProfileSkill.objects.filter(user=self.user))

    def has_skill(self,tag) :
        return self.has_something(self.get_skills,tag)

    def add_skill(self,skill_tag) :
        if not self.has_skill(skill_tag) :
            ps = ProfileSkill(skill=skill_tag,user=self.user)
            ps.save()


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
    logging.debug("in create a profile signal %s" % instance)
    if instance is None:
        return
    print  "CCCCC "
    profile, created = Profile.objects.get_or_create(user=instance)
    print "create_profile for %s, %s, %s" % (instance,profile,created)

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

class InterestTag(models.Model) :

    label = models.TextField(max_length=30)

class ProfileInterest(models.Model) :
    user = models.ForeignKey(User)
    interest = models.ForeignKey(InterestTag)

class SkillTag(models.Model) :
    label = models.TextField(max_length=30)

class ProfileSkill(models.Model) :
    user = models.ForeignKey(User)
    skill = models.ForeignKey(SkillTag)

class NeedTag(models.Model) :
    label = models.TextField(max_length=30)

class ProfileNeed(models.Model) :
    user = models.ForeignKey(User)
    need = models.ForeignKey(NeedTag)
    
