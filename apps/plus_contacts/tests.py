import unittest
import datetime

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import *
from apps.plus_groups.models import *

from models import Contact, Application
from models import PENDING, WAITING_USER_SIGNUP


from apps.plus_permissions.default_agents import get_site, get_admin_user, get_all_members_group, get_anonymous_group
from apps.plus_permissions.interfaces import PlusPermissionsNoAccessException
from apps.plus_permissions.proxy_hmac import attach_hmac

from apps.plus_permissions.models import has_access

from apps.plus_lib.utils import i_debug

from apps.plus_permissions.types.User import create_user

class TestContact(unittest.TestCase):

    def setUp(self):
        u = User(username='phil',email_address='x@y.com')
        u.save()
        ct = Contact(first_name='tom',last_name='salfield',organisation='the-hub',email_address='tom@the-hub.net',location='islington',apply_msg='about me', find_out='through the grapevine',invited_by=u)
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
        u2 = get_admin_user()

        # now upgrade to a user
        u3 = self.ct.become_member('tom.salfield',  invited_by=self.u, accepted_by=u2)
        self.assertEquals(u2.__class__, User)

        # the following commented test was to confirm that becoming a member deleted the Contact
        # as I'm not deleting contacts at the moment, this test is redundant
        # self.assertEquals(len(Contact.objects.filter(id=self.ct.id)), 0)
        
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

        self.assertTrue(u3.is_member_of(get_all_members_group()))


class TestApplication(unittest.TestCase) :

    def count(self,it) :
        count = 0
        for i in it :
            count= count+1
        return count

    #@i_debug
    def test_application(self) :

        god = get_admin_user() # now a standard user, and member of the site_members_group's admin
        site = get_site(god)

        contact = site.create_Contact(god, first_name='kate', last_name='smith', email_address='kate@z.x.com')
        contact.save()

        self.assertTrue(contact.get_inner().get_creator())

        group = site.create_TgGroup(god, group_name='sexy_salad', display_name='Sexy Salad', level='member')
        

        self.assertTrue(group.get_inner().get_creator()) # group should have a creator
        self.assertEquals(group.get_inner().get_creator().id,god.id)
        
        application = site.create_Application(god, applicant=contact, request='I want to join in')
        
        # the following should be true because application was created by god
        # so god is its "creator" and default for Application.Editor is "creator"

        self.assertTrue(has_access(god, application, 'Application.Editor'))
        application.group = group.get_inner()
        application.save()

        self.assertTrue(has_access(group,application,'Application.Viewer'))

        self.assertEquals(application.date.date(),datetime.datetime.today().date())


        self.assertTrue(application.applicant.s_eq(contact))
        self.assertEquals(application.request, 'I want to join in')
        self.assertTrue(application.group.s_eq(group))
        self.assertEquals(application.status, PENDING)
        self.assertEquals(application.admin_comment,'')
        self.assertEquals(application.accepted_by,None)


        # adding a couple more 

        ap2 = site.create_Application(god, applicant=contact,request='ap2',group=get_anonymous_group())
        ap3 = site.create_Application(god, applicant=contact,request='ap3',group=get_all_members_group())
        
        self.assertEquals(self.count(Application.objects.filter()),3)
        self.assertEquals(self.count(Application.objects.filter(request='ap2')),1)

        mable = User(username='mable',email_address='mable@b.com')
        mable.save()
        self.assertEquals(Application.objects.plus_count(mable),0)

        # now there's a security tag which links "group" as context to the interface "ApplicationViewer"
        site.get_inner().get_security_context().add_arbitrary_agent(group, 'Application.Viewer', god)
        
        self.assertTrue(has_access(group, ap2, 'Application.Viewer'))

        self.assertFalse(has_access(mable, ap2, 'Application.Viewer'))

        self.assertEquals(Application.objects.plus_count(group),3)
            
        s_application = Application.objects.plus_get(mable, id=application.id)
        
        def f(application,sponsor) :
            application.accept(sponsor)
        
        self.assertRaises(PlusPermissionsNoAccessException,f,s_application,mable)
            
        self.assertEquals(s_application.get_inner().status,PENDING)

        application = Application.objects.get(id=application.id)

        application.accept(mable, 'site_root', admin_comment='great choice')

        self.assertEquals(application.status,WAITING_USER_SIGNUP)
        self.assertEquals(application.admin_comment,'great choice')
        self.assertEquals(application.accepted_by, mable)

        
class TestInvite(unittest.TestCase) :
    def test_invite(self):
        site = get_site(get_admin_user())
        all_members = get_all_members_group()

        u = create_user('fred','fred@fred.com')
        
        #XXX continue
        #inv1 = site.invite_non_member('fred@fred.com')
        #inv2 = site.invite_non_member('j.bloke@random_mail.com')

        #self.assertTrue(inv1.is_existing_member())
        #self.assertFalse(inv2.is_existing_member())
        
        #self.assertEquals(inv1.get_user().id, u.id)
        #self.assertNone(inv2.get_user())
        
        


