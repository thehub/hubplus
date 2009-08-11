import unittest
import datetime
import simplejson

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User
try :
    from apps.hubspace_compatibility.models import TgGroup, Location, HCGroupMapping
except Exception, e:
    print "*** %s" % e

from models import *
from apps.plus_groups.models import create_hub, create_site_group

from apps.plus_groups import *

import ipdb

# Permission Management by Content Types
from OurPost import *

#  
class TestPermissions(unittest.TestCase) :

    def testGroupHierarchy(self):
        # Test the group hierarchies stuff ...

        # make a user
        u = User(username='nils',email_address='nils@the-hub.net')
        u.save()

        # and a couple more
        u2 = User(username='tom',email_address='tom@the-hub.net')
        u2.save()
    
        u3 = User(username='jesson',email_address='jesson@the-hub.net')
        u2.save()

        # we need location for TgGroups
        l = Location(name='kingsX')
        l.save()

        # here's a group (called "hub-members")
        hubMembers = TgGroup(group_name='hub-members',display_name='members',created=datetime.date.today(),place=l)
        hubMembers.save()

        # they start empty
        self.assertEquals(hubMembers.get_no_members(),0)

        # we now add member to the group
        hubMembers.add_member(u)
        # which now has one member
        self.assertEquals(hubMembers.get_no_members(),1)
        # and u is a member 
        self.assertTrue(u.is_member_of(hubMembers))
        
        # and hubMembers is itself in u's 'enclosures' (containing groups)
        self.assertTrue(hubMembers in set(u.get_enclosures()))

        # check that you can't add the same member twice
        hubMembers.add_member(u)
        self.assertEquals(hubMembers.get_no_members(),1)

        # another group, called hosts
        hosts = TgGroup(group_name='admins',display_name='admins',created=datetime.date.today(),place=l)
        hosts.save()

        # u2 is a host
        hosts.add_member(u2)

        # make hosts a member (sub-group) of hubMembers
        hubMembers.add_member(hosts) 
        
        # and check that it's counted as a member
        self.assertEquals(hubMembers.get_no_members(),2)

        # and hubMembers is in hosts' enclosures
        self.assertTrue(hubMembers in set(hosts.get_enclosures()))

        # and hosts is a member of members
        self.assertTrue(hosts.is_member_of(hubMembers))
        self.assertTrue(u2.is_member_of(hosts))

        # and membership is transitive
        self.assertTrue(u2.is_member_of(hubMembers))
        
        # but we haven't done anything crazy by making is_member_of just return false positives
        self.assertFalse(u.is_member_of(hosts))

        # nevertheless we can use is_direct_member_of to check for membership which is NOT transitive
        self.assertTrue(u2.is_direct_member_of(hosts))
        self.assertFalse(u2.is_direct_member_of(hubMembers))

        # Now we u becomes a member of subgroup hosts ... 
        hosts.add_member(u) 

        # it doesn't stop being a direct_member of hubMembers
        # which seems a bit messy, but it's dangerous to prune this given that membership is a lattice, not a tree
        self.assertTrue(u.is_direct_member_of(hosts))
        self.assertTrue(u.is_direct_member_of(hubMembers))
        self.assertTrue(u.is_member_of(hubMembers))


        another_group,ag_hosts = create_site_group('site_group','Another Site Group', location=l, create_hosts=True)
        another_group.add_member(hubMembers)
        self.assertTrue(ag_hosts.is_member_of(another_group))
        self.assertFalse(another_group.is_member_of(ag_hosts))


        # Now, if we ask for enclosure_set of u, we should get hubMembers and hosts
        es = u.get_enclosure_set()
        print "LL "
        print es
        self.assertTrue(u in es)
        self.assertTrue(hosts in es)
        self.assertTrue(hubMembers in es)
        self.assertTrue(another_group in es)
        self.assertFalse(ag_hosts in es)
        self.assertFalse(u2 in es)


        # now let's see what happens when we remove membership
        hosts.remove_member(u)
        self.assertFalse(u.is_direct_member_of(hosts))
        self.assertFalse(u.is_member_of(hosts))

        



    def testPermissions(self) :
        ps = PermissionSystem()

        u = User(username='synnove',email_address='synnove@the-hub.net')
        u.save()

        agent_type = ContentType.objects.get_for_model(u)
        an_agent = Agent.objects.get(agent_content_type=agent_type,agent_object_id=u.id)
        self.assertEquals(an_agent.agent.id,u.id)

        # two resources, blog and blog2
        blog= OurPost(title='my post')
        blog.set_security_context(blog)
        blog.save()
        blog2 = OurPost(title='another post')
        blog2.set_security_context(blog2)
        blog2.save()

        l = Location(name='da hub')
        l.save()

        editors = TgGroup(group_name='editors',display_name='editors',created=datetime.date.today(),place=l)
        editors.save()

        tif = self.makeInterfaceFactory()

        # explicit tag between u, blog, viewer
        t = SecurityTag(context=blog,interface=tif.get_id(OurPost,'Viewer'))
        t.save()

        t.agents.add(u.corresponding_agent())
        t.save()
        
        IViewer = tif.get_id(OurPost,'Viewer')
        ICommentor = tif.get_id(OurPost,'Commentor')
        IEditor = ps.get_interface_id(OurPost,'Editor')

        self.assertTrue(ps.has_access(u,blog,IViewer))

        t2 = ps.create_security_tag(blog,ICommentor,[u])

        self.assertTrue(ps.has_access(u,blog,ICommentor))

        self.assertFalse(ps.has_access(u,blog,IEditor))


        t3 = ps.create_security_tag(blog2,IEditor,[editors])
        
        self.assertTrue(ps.has_access(editors,blog2,IEditor))

        editors.add_member(u)

        self.assertTrue(ps.has_access(u,blog2,IEditor))
        self.assertFalse(ps.has_access(u,blog,IEditor))

        self.assertFalse(ps.direct_access(u,blog2,IEditor))
        self.assertTrue(ps.direct_access(u,blog,IViewer))

        t2.delete()
       
        self.assertFalse(ps.has_access(u,blog,ICommentor))
        ps.delete_access(u,blog,IViewer)

        self.assertFalse(ps.has_access(u,blog,IViewer))

        # now let's test contexts
        discussion_group,discussion_admin = create_site_group('discussion','Discussion',l)
        blog3 = OurPost(title='story')
        blog3.set_container(discussion_group)
        blog3.set_security_context(discussion_group)
        blog3.save()
        
        ps.create_security_tag(discussion_group,IViewer,[u])
        self.assertTrue(ps.has_access(u,blog3,IViewer))
        self.assertFalse(ps.has_access(u,blog3,IEditor))
        
        # and group
        ps.create_security_tag(discussion_group,IEditor,[editors])
        self.assertTrue(ps.has_access(u,blog3,IEditor))
        
                         


    def makeInterfaceFactory(self) :
        ps = PermissionSystem()
        tif = ps.get_interface_factory()        
        tif.add_permission_manager(OurPost,OurPostPermissionManager(OurPost))
        return tif


    def testInterfaces(self) :

        tif = self.makeInterfaceFactory()

        class A : pass
        self.assertTrue(tif.get_type(OurPost))
        self.assertRaises(Exception,tif.get_type,A)

        self.assertEquals(tif.get_interface(OurPost,'Viewer'),OurPostViewer)
        self.assertRaises(Exception,tif.get_interface,OurPost,'xyz')

        blog= OurPost(title='what I want to say',body="Here's what")
        blog.save()
        blog2 = blog
        
        blog = NullInterface(blog)
        def f(blog) : return blog.title
        
        self.assertRaises(PlusPermissionsNoAccessException,f,blog) 
        try : f(blog)
        except PlusPermissionsNoAccessException, e :
            self.assertEquals(e.silent_variable_failure,True)


        class BodyViewer(Interface) :
            body = InterfaceReadProperty('body')

        
        blog.add_interface(BodyViewer)
        self.assertEquals(blog.body,"Here's what")
        self.assertRaises(PlusPermissionsNoAccessException,f,blog)

        blog.add_interface( tif.get_interface(OurPost,'Viewer'))
        self.assertEquals(blog.title,'what I want to say')
        
        def f(blog) : blog.title = "something stupid"
        self.assertRaises(PlusPermissionsReadOnlyException,f,blog)
        
        def try_delete(blog) : 
            blog.delete()
        self.assertRaises(PlusPermissionsNoAccessException,try_delete,blog)

        blog.add_interface( tif.get_interface(OurPost,'Editor'))
        
        blog.title = "Hello"
        self.assertEquals(blog.title,'Hello')
        blog.save()

        self.assertEquals(blog2.title,'Hello')

        blog.remove_interface( tif.get_interface(OurPost,'Editor'))
        self.assertRaises(PlusPermissionsReadOnlyException,f,blog)
        
        self.assertRaises(PlusPermissionsNoAccessException,try_delete,blog)
        blog.add_interface(tif.get_interface(OurPost,'Editor'))

        def foo(r) :
            r.foo()
        self.assertRaises(PlusPermissionsNoAccessException,foo,blog)
        
        class FooRunner(Interface) :
            foo = InterfaceCallProperty('foo')
        
        blog.add_interface(FooRunner)
        blog.foo()

        blog.delete()
        


    def testProfileSignals(self) :
        from Profile import *
        u = User(username='jesson',email='',password='abc')
        u.save()
        p = u.get_profile()
        p.about='about jesson'
        p.save()
        ps = PermissionSystem()
        self.assertTrue(ps.has_access(ps.get_anon_group(),p,ps.get_interface_factory().get_id(Profile,'Viewer')))



    def test_contexts(self) :
        blog = OurPost(title='hello')
        location = Location(name='world')
        location.save()
        group,hosts = create_site_group('group','Our Group',location=location,create_hosts=True)
        blog.set_security_context(group)
        self.assertEquals(Context.objects.get_security_context(blog).id, group.id)
        blog.set_context(hosts)
        self.assertEquals(Context.objects.get_context(blog).id,hosts.id)
       
        #ipdb.set_trace()
        Context.objects.set_security_context(blog,blog)
        
        print Context.objects.all()
        
        print "RR",blog.get_security_context()
        
        self.assertEquals(blog.get_security_context().id, blog.id)
        self.assertEquals(blog.get_context().id, group.id)
    
        class A(ContextMixin) : pass
        




    def test_group_admin(self) :
        l = Location(name='Dalston')
        l.save()
        g, h = create_hub(name='hub-dalston',display_name='Hub Dalston', location=l, create_hosts=True)


        
