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
        


    def testDelegates(self) :
        u = User(username='ck')
        u.save()
        p=u.get_profile()
        u=p.user

        p.name = 'ck-name'
        self.assertEquals(p.name,'ck-name')

        p.display_name = p.name

        self.assertEquals(p.display_name,p.name)
        self.assertEquals(p.user.display_name,p.name)
        self.assertEquals(p.user,u)

        self.assertEquals(u.display_name,p.name)

        p.save()


    
