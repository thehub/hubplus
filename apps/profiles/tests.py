import unittest

from django.db import models
from django.contrib.auth.models import *
from models import *

from apps.plus_permissions.default_agents import get_admin_user, get_site

def gensize(gen) :
    count = 0
    for x in gen : 
        count = count +1
    return count


class PermissionedProfiles(unittest.TestCase):
    def test_pp(self):
        god = get_admin_user()
        site = get_site(god)
        u = User(username='patrick', email_address='patrick@the-hub.net')
        u.save()
        p = u.get_profile()
        self.assertTrue(p.get_ref())
        self.assertEquals(p.get_security_context(),site.get_inner().get_security_context())
        


class TestProfileSubsidiaries(unittest.TestCase):


    
    def testHostInfo(self) :
        # make sure a HostInfo record is created when a User is saved
        u = User(username='bob',email_address='bob@the-hub.net')
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


    
