
import unittest
import datetime

from django.db import models

from django.contrib.auth.models import User
try :
    from apps.hubspace_compatibility.models import TgGroup, Location, HCGroupMapping
except Exception, e:
    print "*** %s" % e

from models import *

import pdb

# Permission Management by Content Types
from OurPost import *

# 
class TestPermissions(unittest.TestCase) :

    def testGroupHierarchy(self):
        u = User()
        u.username = 'nils'
        u.save()

        u2 = User()
        u2.username='tom'
        u2.save()
    
        u3 = User()
        u3.username = 'jesson'
        u2.save()

        print User.objects.all()

        l = Location(name='kingsX')
        l.save()

        g = TgGroup(group_name='members',display_name='members',created=datetime.date.today(),place=l)
        g.save()

        self.assertEquals(g.get_no_members(),0)
        g.add_member(u)
        self.assertEquals(g.get_no_members(),1)
        self.assertTrue(u.is_member_of(g))
        
        self.assertTrue(g in set(u.get_enclosures()))

        g.add_member(u)
        self.assertEquals(g.get_no_members(),1)

        g2 = TgGroup(group_name='admins',display_name='admins',created=datetime.date.today(),place=l)
        g2.save()

        g2.add_member(u2)

        g.add_member(g2) # make group B a member or subgroup of A
        self.assertEquals(g.get_no_members(),2)
        self.assertTrue(g in set(g2.get_enclosures()))
        self.assertTrue(g2.is_member_of(g))
        self.assertTrue(u2.is_member_of(g2))
        self.assertTrue(u2.is_member_of(g))

        self.assertFalse(u.is_member_of(g2))

        self.assertTrue(u2.is_direct_member_of(g2))
        self.assertFalse(u2.is_direct_member_of(g))

        g2.add_member(u)
        self.assertTrue(u.is_direct_member_of(g2))
        self.assertFalse(u.is_direct_member_of(g))
        self.assertTrue(u.is_member_of(g))


    def testPermissions(self) :
        u = User(username='synnove')
        u.save()

        blog= OurPost(title='my post')
        blog.save()
        blog2 = OurPost(title='another post')
        blog2.save()

        l = Location(name='da hub')
        l.save()

        editors = TgGroup(group_name='editors',display_name='editors',created=datetime.date.today(),place=l)
        editors.save()

        tif = self.makeInterfaceFactory()

        t = SecurityTag(name='tag1',agent=u,resource=blog,interface=tif.get_id(OurPost,'Viewer'))
        t.save()

        t2 = SecurityTag(name='tag1',agent=u,resource=blog,interface=tif.get_id(OurPost,'Commentor'))
        t2.save()

        self.assertTrue(t.has_access(u,blog,tif.get_id(OurPost,'Commentor')))
        self.assertFalse(t2.has_access(u,blog,tif.get_id(OurPost,'Editor')))

        t3 = SecurityTag(name='tag1',agent=editors,resource=blog2,interface=tif.get_id(OurPost,'Editor'))
        t3.save()

        self.assertTrue(t3.has_access(editors,blog2,tif.get_id(OurPost,'Editor')))

        editors.add_member(u)

        self.assertTrue(t3.has_access(u,blog2,tif.get_id(OurPost,'Editor')))
        self.assertFalse(t3.has_access(u,blog,tif.get_id(OurPost,'Editor')))

        self.assertEquals(len([x for x in t3.all_named()]),3)



    def makeInterfaceFactory(self) :
        ps = PermissionSystem()
        tif = ps.get_interface_factory()        
        tif.add_permission_manager(OurPost,OurPostPermissionManager())
        return tif


    def testInterfaces(self) :
        tif = self.makeInterfaceFactory()

        class A : pass
        self.assertTrue(tif.get_type(OurPost))
        self.assertRaises(Exception,tif.get_type,A)

        self.assertEquals(tif.get_interface(OurPost,'Viewer'),OurPostViewer)
        self.assertRaises(Exception,tif.get_interface,OurPost,'xyz')
        

    def testSliderSet(self) :
        tif = self.makeInterfaceFactory()
        ps = PermissionSystem()
        l = Location(name='biosphere')
        l.save()

        group = TgGroup(group_name='greenarchitects',display_name='Green Architects', place=l,created=datetime.date.today())
        group.save()
        adminGroup = TgGroup(group_name='gaadmin', display_name='Green Architecture Admin', place=l,created=datetime.date.today())
        adminGroup.save()

        da = DefaultAdmin(agent=adminGroup,resource=group)
        da.save()

        blog = OurPost(title='test')
        blog.save()
        u = User(username='phil')
        u.save()
        author = User(username='author')
        author.save()

        everyone = ps.get_anon_group()
        everyone.add_member(u)
        everyone.add_member(author)

        all_members = ps.get_all_members_group()

        # NB : todo
        # we have to find solution to making all users members of everyone, either
        # 1) automatically add all users to root group
        # 2) when testing permissions, resources which are linked to this group, we don't bother testing agent
        # Both have pros and cons
        # 1) pro is that we have simpler permission system rules. Just test the existence of security tags
        # 1) con is that we have more complicated set-up. When do we hang users off everyone? When they're created? What about legacy? etc. 
        # What if they're already members of sub-groups etc?
        # 2) pro - we don't have to solve the cons of 1
        # 2) con, we add more complex logic to the permission test which may, spiral out of control

        # ok, back to the tests

        pm = tif.get_permission_manager(OurPost)
        pd = pm.setup_defaults(blog,author,group)

        self.assertFalse(pd.has_extras())
        self.assertFalse(pd.is_changed())
        self.assertEquals(len(pd.get_sliders()),3)
        s = pd.get_slider('Viewer')
        self.assertEquals(len(s.get_options()),4)
        ops = s.get_options()

        # who are the groups in the default slider sequence?
        # if there's an official "admin" group for another group (or resource) how is this represented?
        # if we use current permission mechanism, then this allows many admins over a group
        # but that is too ambiguous to infer the defaults for the sliders.

        self.assertEquals([a.name for a in ops],['root','all_members','Green Architects','Green Architecture Admin','author'])
        self.assertEquals(s.get_current_option().name,'root')
        tags = ps.get_permissions_for(blog)

        self.assertTrue(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Editor')))
        self.assertTrue(ps.has_access(u,blog,tif.get_id(OurPost,'Viewer')))

        s.set_current_option(1) # is it ok to set option using numeric index? Or better with name?
        self.assertEquals(s.get_current_option().name,'all_members')
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(members,blog,tif.get_id(OurPost,'Viewer')))
