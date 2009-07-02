import unittest

from django.db import models
from django.contrib.auth.models import *
from models import *


def gensize(gen) :
    count = 0
    for x in gen : 
        count = count +1
    return count

class TestProfileSubsidiaries(unittest.TestCase):

    def testHostInfo(self) :
        # make sure a HostInfo record is created when a User is saved
        u = User(username='bob')
        u.save()
        p = u.get_profile()
        hi = p.get_host_info()
        self.assertEquals(hi.user,u)
        

    def testInterestsNeedsAndSkills(self) :
        # Needs, Skills and Interests all work the same way
        # But have their own Model classes (NeedTag,SkillTag,InterestTag respectively)
        u = User(username='gustavo')
        u.save()
        p = u.get_profile()

        # Interests
        self.assertFalse(p.has_interests())
        self.assertEquals(gensize(p.get_interests()),0)

        il = InterestTag(label='green architecture')
        il.save()

        p.add_interest(il)

        self.assertTrue(p.has_interests())
        self.assertEquals(gensize(p.get_interests()),1)
        self.assertTrue(p.has_interest(il))
        
        self.assertEquals(get_or_create_interest('green architecture')[0],il)
        x, created = get_or_create_interest('ethical jewelry')
        self.assertEquals(get_or_create_interest('ethical jewelry')[0],x)
        self.assertTrue(created)
                          
        # Skills
        self.assertFalse(p.has_skills())
        self.assertEquals(gensize(p.get_skills()),0)
        
        sl = SkillTag(label='grass roofs')
        sl.save()
        
        p.add_skill(sl)

        self.assertTrue(p.has_skills())
        self.assertEquals(gensize(p.get_skills()),1)
        self.assertTrue(p.has_skill(sl))
        
        self.assertEquals(get_or_create_skill('grass roofs')[0],sl)
        x,created = get_or_create_skill('plumbing')
        self.assertEquals(get_or_create_skill('plumbing')[0],x)
        self.assertTrue(created)

    
        # Needs
        nl = NeedTag(label='botany')
        nl.save()

        self.assertFalse(p.has_needs())
        self.assertEquals(gensize(p.get_needs()),0)

        p.add_need(nl)

        self.assertTrue(p.has_needs())
        self.assertEquals(gensize(p.get_needs()),1)
        self.assertTrue(p.has_need(nl))

        self.assertEquals(get_or_create_need('botany')[0],nl)
        x, created = get_or_create_need('history')
        self.assertEquals(get_or_create_need('history')[0],x)
        self.assertTrue(created)

    def testDelegates(self) :
        u = User(username='ck')
        u.save()
        p=u.get_profile()
        p.save()
        u=p.user

        self.assertEquals(p,u.get_profile())
        self.assertEquals(p.user,u)
        self.assertTrue(p.user is u)

        p.role = 'host'
        self.assertEquals(p.role,u.title)
        self.assertEquals(p.user.title,p.role)
        self.assertEquals(p.user,u)
        self.assertEquals(u.title,p.role)

        self.assertEquals(u.title,p.role)
        u.title = 'coffee maker'
        self.assertEquals(u.title,p.role)


        

