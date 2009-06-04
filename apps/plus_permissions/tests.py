
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

        members = TgGroup(group_name='members',display_name='members',created=datetime.date.today(),place=l)
        members.save()

        self.assertEquals(members.get_no_members(),0)
        members.add_member(u)
        self.assertEquals(members.get_no_members(),1)
        self.assertTrue(u.is_member_of(members))
        
        self.assertTrue(members in set(u.get_enclosures()))

        members.add_member(u)
        self.assertEquals(members.get_no_members(),1)

        hosts = TgGroup(group_name='admins',display_name='admins',created=datetime.date.today(),place=l)
        hosts.save()

        hosts.add_member(u2)

        members.add_member(hosts) # make hosts a member or subgroup of members
        self.assertEquals(members.get_no_members(),2)
        self.assertTrue(members in set(hosts.get_enclosures()))
        self.assertTrue(hosts.is_member_of(members))
        self.assertTrue(u2.is_member_of(hosts))
        self.assertTrue(u2.is_member_of(members))

        self.assertFalse(u.is_member_of(hosts))

        self.assertTrue(u2.is_direct_member_of(hosts))
        self.assertFalse(u2.is_direct_member_of(members))

        # Now u becomes a member of subgroup hosts ... 
        # Question, can we move it from "members" ... it seems it would by good (don't leave junk data in the database)
        # but "smells" dangerous ... 

        hosts.add_member(u) 
        self.assertTrue(u.is_direct_member_of(hosts))
        self.assertTrue(u.is_direct_member_of(members))
        self.assertTrue(u.is_member_of(members))


    def testPermissions(self) :
        ps = PermissionSystem()

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

        self.assertTrue(t2.has_access(u,blog,tif.get_id(OurPost,'Commentor')))
        self.assertFalse(t2.has_access(u,blog,tif.get_id(OurPost,'Editor')))

        t3 = SecurityTag(name='tag1',agent=editors,resource=blog2,interface=tif.get_id(OurPost,'Editor'))
        t3.save()

        self.assertTrue(ps.has_access(editors,blog2,tif.get_id(OurPost,'Editor')))

        editors.add_member(u)

        self.assertTrue(ps.has_access(u,blog2,tif.get_id(OurPost,'Editor')))
        self.assertFalse(ps.has_access(u,blog,tif.get_id(OurPost,'Editor')))

        self.assertEquals(len([x for x in t3.all_named()]),3)

        t2.delete()
        
        self.assertFalse(ps.has_access(u,blog,tif.get_id(OurPost,'Commentor')))
        ps.delete_access(u,blog,tif.get_id(OurPost,'Viewer'))

        self.assertFalse(ps.has_access(u,blog,tif.get_id(OurPost,'Viewer')))

        

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
        

    def testSliders(self) :
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

        pm = ps.get_permission_manager(OurPost)

        self.assertFalse(pd.has_extras())
        self.assertFalse(pd.is_changed())
        self.assertEquals(len(pd.get_sliders()),3)
         
        s = pm.make_slider(blog,'Viewer',group,author)

        self.assertEquals(len(s.get_options()),5)
        ops = s.get_options()

        self.assertEquals([a.name for a in ops],['root','all_members','Green Architects','author','Green Architecture Admin'])
        self.assertEquals(s.get_current_option().name,'root')
        tags = ps.get_permissions_for(blog)

        self.assertTrue(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Editor')))
        self.assertTrue(ps.has_access(u,blog,tif.get_id(OurPost,'Viewer')))

        s.set_current_option(1) # is it ok to set option using numeric index? Or better with name?
        self.assertEquals(s.get_current_option().name,'all_members')
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(members,blog,tif.get_id(OurPost,'Viewer')))

        


