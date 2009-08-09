import unittest
import datetime

from django.db import models


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from apps.plus_permissions.models import *
from django.contrib.auth.models import *

from models import *

from apps.plus_permissions import *

class TestContact(unittest.TestCase):

    def setUp(self):
        u = User(username='phil',email_address='x@y.com')
        u.save()
        ct = PlusContact(first_name='tom',last_name='salfield',organisation='the-hub',email='tom@the-hub.net',location='islington',apply_msg='about me', find_out='through the grapevine',invited_by=u)
        ct.save()
        self.u = u
        self.ct = ct
        return

    def tearDown(self):
        self.u.delete()
        if self.ct.id:
            self.ct.delete()
            

    def test_contact(self):
        self.assertEquals(self.ct.first_name,'tom')

        self.assertEquals(self.ct.find_out,'through the grapevine')
        self.assertEquals(self.ct.invited_by.username,'phil')

    def test_become_member(self):
        u2 = User(username='admin',email_address='y@y.com')
        u2.save()
        # now upgrade to a user
        u3 = self.ct.become_member('tom.salfield',  invited_by=self.u, accepted_by=u2)
        self.assertEquals(u2.__class__, User)
        self.assertEquals(len(PlusContact.objects.filter(id=self.ct.id)), 0)
        p = u3.get_profile()
        self.assertEquals(p.first_name, self.ct.first_name)
        self.assertEquals(p.last_name, self.ct.last_name)
        self.assertEquals(p.email_address, self.ct.email)
        self.assertEquals(p.location, self.ct.location)
        self.assertEquals(p.get_host_info().find_out, self.ct.find_out)
        self.assertTrue(p.was_invited())
        self.assertTrue(p.was_accepted())
        self.assertEquals(p.invited_by.username, self.u.username)
        self.assertEquals(p.accepted_by.username, u2.username)

        ps = get_permission_system()
        self.assertTrue(u3.is_member_of(ps.get_all_members_group()))
