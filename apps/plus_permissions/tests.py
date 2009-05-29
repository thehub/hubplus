
import unittest
import datetime

from django.db import models

from django.contrib.auth.models import User
try :
    from apps.hubspace_compatibility.models import TgGroup, Location, HCGroupMapping
except Exception, e:
    print "*** %s" % e

from models import *


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

        self.assertEquals(g.getNoMembers(),0)
        g.addMember(u)
        self.assertEquals(g.getNoMembers(),1)
        self.assertTrue(u.isMemberOf(g))
        
        self.assertTrue(g in set(u.getEnclosures()))

        g.addMember(u)
        self.assertEquals(g.getNoMembers(),1)

        g2 = TgGroup(group_name='admins',display_name='admins',created=datetime.date.today(),place=l)
        g2.save()

        g2.addMember(u2)

        g.addMember(g2) # make group B a member or subgroup of A
        self.assertEquals(g.getNoMembers(),2)
        self.assertTrue(g in set(g2.getEnclosures()))
        self.assertTrue(g2.isMemberOf(g))
        self.assertTrue(u2.isMemberOf(g2))
        self.assertTrue(u2.isMemberOf(g))

        for x in HCGroupMapping.objects.all() :
            print '%s, %s' % (x.parent.group_name,x.child)

        self.assertFalse(u.isMemberOf(g2))

        self.assertTrue(u2.isDirectMemberOf(g2))
        self.assertFalse(u2.isDirectMemberOf(g))

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

        for y in (x for x in SecurityTag.objects.all() ) :
            print y

        self.assertTrue(t.has_access(u,blog,tif.get_id(OurPost,'Commentor')))
        self.assertFalse(t2.has_access(u,blog,tif.get_id(OurPost,'Editor')))

        t3 = SecurityTag(name='tag1',agent=editors,resource=blog2,interface=tif.get_id(OurPost,'Editor'))
        t3.save()

        self.assertTrue(t3.has_access(editors,blog2,tif.get_id(OurPost,'Editor')))

        editors.addMember(u)

        self.assertTrue(t3.has_access(u,blog2,tif.get_id(OurPost,'Editor')))
        self.assertFalse(t3.has_access(u,blog,tif.get_id(OurPost,'Editor')))

        self.assertEquals(len([x for x in t3.all_named()]),3)

    def makeInterfaceFactory(self) :
        tif = InterfaceFactory()
        
        tif.add_type(OurPost)
        tif.add_interface(OurPost,'Viewer',OurPostViewer)
        tif.add_interface(OurPost,'Editor',OurPostEditor)
        tif.add_interface(OurPost,'Commentor',OurPostCommentor)
        return tif

    def testInterfaces(self) :
        tif = self.makeInterfaceFactory()

        class A : pass
        self.assertTrue(tif.get_type(OurPost))
        self.assertRaises(Exception,tif.get_type,A)

        self.assertEquals(tif.get_interface(OurPost,'Viewer'),OurPostViewer)
        self.assertRaises(Exception,tif.get_interface,OurPost,'xyz')
        

