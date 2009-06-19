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
        u = User(username='bob')
        u.save()
        p = u.get_profile()
        hi = p.get_host_info()
        self.assertEquals(hi.user,u)
        

    def testInterestsNeedsAndSkills(self) :
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
        
        # Skills
        self.assertFalse(p.has_skills())
        self.assertEquals(gensize(p.get_skills()),0)
        
        sl = SkillTag(label='grass roofs')
        sl.save()
        
        p.add_skill(sl)

        self.assertTrue(p.has_skills())
        self.assertEquals(gensize(p.get_skills()),1)
        self.assertTrue(p.has_skill(sl))
    
        # Needs
        nl = NeedTag(label='botany')
        nl.save()

        self.assertFalse(p.has_needs())
        self.assertEquals(gensize(p.get_needs()),0)

        p.add_need(nl)

        self.assertTrue(p.has_needs())
        self.assertEquals(gensize(p.get_needs()),1)
        self.assertTrue(p.has_need(nl))

