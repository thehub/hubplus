
import unittest

from django.db import models

from django.contrib.auth.models import User
try :
    from apps.hubspace_compatibility.models import TgGroup
except Exception, e:
    print "*** %s" % e

from models import *


class TestPermissions(unittest.TestCase) :

    def testNew(self) :
        u = User(username='synnove')

        blog= BlogPost('my post')
        blog2 = BlogPost('another post')

        editors = TgGroup(group_name='editors',display_name='editors')

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
