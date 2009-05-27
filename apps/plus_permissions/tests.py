
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


    def testNew(self) :
        u = User(username='synnove')
        u.save()

        blog= BlogPost('my post')
        blog2 = BlogPost('another post')

        l = Location(name='da hub')
        l.save()

        editors = TgGroup(group_name='editors',display_name='editors',created=datetime.date.today(),place=l)
        editors.save()

        self.assertTrue(BlogPost.interfaces['viewer'])
        self.assertTrue(BlogPost.interfaces['editor'])
        self.assertTrue(BlogPost.interfaces['commentor'])

        t = SecurityTag('tag1')
        t.giveAccess(u,blog,BlogPost.interfaces['viewer'])
        t.giveAccess(u,blog,'commentor')

        self.assertTrue(t.hasAccess(u,blog,'commentor'))
        self.assertFalse(t.hasAccess(u,blog,BlogPost.interfaces['editor']))

        t.giveAccess(editors,blog2,'editor')
        self.assertTrue(t.hasAccess(editors,blog2,BlogPost.interfaces['editor']))
        editors.addMember(u)
        self.assertTrue(t.hasAccess(u,blog2,BlogPost.interfaces['editor']))
        self.assertFalse(t.hasAccess(u,blog,BlogPost.interfaces['editor']))
