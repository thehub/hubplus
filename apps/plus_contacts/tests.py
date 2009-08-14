import unittest
import datetime

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import *
from apps.plus_groups.models import *

from models import *

from apps.plus_permissions.models import *
from apps.plus_permissions.Application import *

ps = get_permission_system()

class TestContact(unittest.TestCase):

    def setUp(self):
        u = User(username='phil',email_address='x@y.com')
        u.save()
        ct = PlusContact(first_name='tom',last_name='salfield',organisation='the-hub',email_address='tom@the-hub.net',location='islington',apply_msg='about me', find_out='through the grapevine',invited_by=u)
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
        ps = get_permission_system()
        ps.__init__()
        print TgGroup.objects.all()

        u2 = User(username='admin',email_address='y@y.com')
        u2.save()
        # now upgrade to a user
        u3 = self.ct.become_member('tom.salfield',  invited_by=self.u, accepted_by=u2)
        self.assertEquals(u2.__class__, User)
        self.assertEquals(len(PlusContact.objects.filter(id=self.ct.id)), 0)
        p = u3.get_profile()
        self.assertEquals(p.first_name, self.ct.first_name)
        self.assertEquals(p.last_name, self.ct.last_name)
        self.assertEquals(p.email_address, self.ct.email_address)
        self.assertEquals(p.location, self.ct.location)
        self.assertEquals(p.get_host_info().find_out, self.ct.find_out)
        self.assertTrue(p.was_invited())
        self.assertTrue(p.was_accepted())
        self.assertEquals(p.invited_by.username, self.u.username)
        self.assertEquals(p.accepted_by.username, u2.username)

        ps = get_permission_system()
        self.assertTrue(u3.is_member_of(ps.get_site_members()))


class TestApplication(unittest.TestCase) :

    def count(self,it) :
        count = 0
        for i in it :
            count= count+1
        return count

    def test_application(self) :
        ps = get_permission_system()
        ps.__init__()
        print TgGroup.objects.all()

        contact = PlusContact(first_name='kate', last_name='smith', email_address='kate@z.x.com')
        contact.save()
        group, admin = create_site_group('singing', 'Singers')
        # use make_application to add security_context when creating an application object
        application = make_application(applicant=contact, request='I want to join in',security_context=group)
        application.group = group
        application.save()
        
        self.assertEquals(application.date.date(),datetime.datetime.today().date())
        self.assertEquals(application.applicant, contact)
        self.assertEquals(application.request, 'I want to join in')
        self.assertEquals(application.group, group)
        self.assertEquals(application.status, PENDING)
        self.assertEquals(application.admin_comment,'')
        self.assertEquals(application.accepted_by,None)

        self.assertTrue(ps.has_access(ps.get_site_members(),application,ps.get_interface_id(Application,'Viewer')))
        self.assertTrue(ps.has_access(ps.get_site_members(),application,ps.get_interface_id(Application,'Accepter')))

        ps = get_permission_system()
        # adding a couple more 
        ap2 = make_application(applicant=contact,request='ap2',group=ps.get_anon_group(),security_context=group)
        ap3 = make_application(applicant=contact,request='ap3',group=ps.get_site_members(),security_context=group)
        
        self.assertEquals(self.count(Application.objects.filter()),3)
        self.assertEquals(self.count(Application.objects.filter(request='ap2')),1)

        u = User(username='mable',email_address='mable@b.com')
        u.save()
        self.assertEquals(self.count(Application.objects.filter(permission_agent=u)),0)

        # now there's a security tag which links "group" as context to the interface "PlusApplicationViewer"
        t = ps.create_security_tag(group,ps.get_interface_id(Application,'Viewer'),[u])
        t.save()
        
        self.assertEquals(self.count(Application.objects.filter(permission_agent=u)),3)
        
