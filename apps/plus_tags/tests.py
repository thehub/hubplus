import unittest

from django.db import models
from django.contrib.auth.models import *
from models import *

from apps.profiles.models import *


def gensize(gen) :
    count = 0
    for x in gen :
        count = count +1
    return count

class TestGenericTags(unittest.TestCase):
    def testTags(self) :
        u = User(username='phil')
        u.save()
        p = u.get_profile()
        u = p.user
        p.save()
        
        (tag,created) = tag_add(p,"test_type","cool",u)
        self.assertEquals(tag.keyword,"cool")
        self.assertEquals(tag.tag_type,"test_type")
        self.assertEquals(tag.agent,u)
        self.assertEquals(tag.subject,p)
        self.assertTrue(created)
        
        (tag2,created)= tag_add(p,"test_type","cool",u) 
        self.assertEquals(tag,tag2)
        self.assertFalse(created)
        tag_delete(p,"test_type","cool",u)
        xs = get_tags(p,"test_type","cool",u)
        count = 0
        for x in xs : count=count+1
        self.assertEquals(count,0)
        



