import unittest
import datetime

from django.db import models

from django.contrib.auth.models import User
try :
    from apps.hubspace_compatibility.models import TgGroup, Location, HCGroupMapping
except Exception, e:
    print "*** %s" % e

from models import *

import ipdb

# Permission Management by Content Types
from OurPost import *

# 
class TestPermissions(unittest.TestCase) :

    def testGroupHierarchy(self):
        # Test the group hierarchies stuff ...

        # make a user
        u = User()
        u.username = 'nils'
        u.save()

        # and a couple more
        u2 = User()
        u2.username='tom'
        u2.save()
    
        u3 = User()
        u3.username = 'jesson'
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

        # now let's see what happens when we remove membership
        hosts.remove_member(u)
        self.assertFalse(u.is_direct_member_of(hosts))
        self.assertFalse(u.is_member_of(hosts))


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

        # confirm that there are no permissions currently relating to this resource
        self.assertFalse(ps.has_permissions(blog))

        t = SecurityTag(name='tag1',agent=u,resource=blog,interface=tif.get_id(OurPost,'Viewer'))
        t.save()

        # confirm that there now are permissions for the resource
        self.assertTrue(ps.has_permissions(blog))

        t2 = SecurityTag(name='tag1',agent=u,resource=blog,interface=tif.get_id(OurPost,'Commentor'))
        t2.save()

        self.assertTrue(ps.has_access(u,blog,tif.get_id(OurPost,'Commentor')))

        self.assertFalse(ps.has_access(u,blog,tif.get_id(OurPost,'Editor')))

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

        self.assertFalse(ps.has_access(u,blog,ps.get_interface_id(OurPost,'Viewer')))

        

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

        blog= OurPost(title='what I want to say',body="Here's what")
        blog.save()
        blog2 = blog
        
        blog = NullInterface(blog)
        def f(blog) : return blog.title
        self.assertRaises(PlusPermissionsNoAccessException,f,blog)

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
        
        blog.delete()
        
        

 

    def testSliders(self) :
        # PermissionSystem is the generic API to the permission system, 
        # it's where you can find most things you need.
        ps = PermissionSystem()

        # Locations currently mandatory for TgGroups, so let's have one
        l = Location(name='biosphere')
        l.save()

        # create a default group
        group = TgGroup(group_name='greenarchitects',display_name='Green Architects', place=l,created=datetime.date.today())
        group.save()

        # create another group to be admin of the first
        adminGroup = TgGroup(group_name='gaadmin', display_name='Green Architecture Admin', place=l,created=datetime.date.today())
        adminGroup.save()

        # set adminGroup to be the admin for group (there should probably be a method of PermissionSystem for this?)
        da = DefaultAdmin(agent=adminGroup,resource=group)
        da.save()

        # create an example bit of content, a blog post of type "OurPost"
        blog = OurPost(title='test')
        blog.save()

        # create a user 
        u = User(username='phil')
        u.save()

        # another user (called 'author') who is set as the creator of our blog
        author = User(username='author')
        author.display_name = 'author'
        author.save()

        # a group which is the top-level of our hierarchy of permission groups. everybody and anybody (even non-authenticated members of the public) 
        # are considered to be members of this group
        everyone = ps.get_anon_group()

        # all_members is all *members* of hubplus, anyone with an account
        all_members = ps.get_all_members_group()

        # the mermissions manager object for OurPosts
        pm = ps.get_permission_manager(OurPost)

        # the permission manager for OurPost knows how to make relevant sliders. 
        # we need to pass to it the resource itself, the name of the interface, 
        #     the agent which is the "owner" of the resource (in this case "group") and 
        #     the agent which is the "creator" of the resource (in this case "author")
        s = pm.make_slider(blog,'Viewer',group,author)

        # now we're just testing that OurPost.Viewer has 5 options for the slider
        self.assertEquals(len(s.get_options()),5)

        # let's see them
        ops = s.get_options()
        self.assertEquals([a.name for a in ops],['root','all_members','Green Architects','author','Green Architecture Admin'])

        # and check that it gave us "root" (ie. the everyone group) as the view default. (we assume that blogs default to allowing non members to read them)
        self.assertEquals(s.get_current_option().name,'root')

        tif = ps.get_interface_factory()
        
        self.assertTrue(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Editor')))
        self.assertTrue(ps.has_access(u,blog,tif.get_id(OurPost,'Viewer')))

        # now use the slider to *change* the permission. Behind the scenes this is manipulating SecurityTags.
        s.set_current_option(1) # is it ok to set option using numeric index? Or better with name?
        self.assertEquals(s.get_current_option().name,'all_members')
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(all_members,blog,tif.get_id(OurPost,'Viewer')))

        # and again
        s.set_current_option(2) # group level
        self.assertEquals(s.get_current_option().name,'Green Architects')
        self.assertFalse(ps.has_access(all_members,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(group,blog,tif.get_id(OurPost,'Viewer'))) 

        # and again
        s.set_current_option(3) # author
        self.assertEquals(s.get_current_option().name,'author')
        self.assertFalse(ps.has_access(group,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(author,blog,tif.get_id(OurPost,'Viewer')))

        # and again
        s.set_current_option(4) # group level
        self.assertEquals(s.get_current_option().name,'Green Architecture Admin')
        self.assertFalse(ps.has_access(author,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(adminGroup,blog,tif.get_id(OurPost,'Viewer')))


    def testProfileSignals(self) :
        from Profile import *
        u = User(username='jesson',email='',password='abc')
        u.save()
        p = u.get_profile()
        p.about='about jesson'
        p.save()
        ps = PermissionSystem()
        self.assertTrue(ps.has_access(ps.get_anon_group(),p,ps.get_interface_factory().get_id(Profile,'Viewer')))


    def testUserWrapping(self) :
        u=User(username='oli')
        u.save()
        blog = OurPost(title='test wrapping')
        blog.save()

        blog = NullInterface(blog)

        ps = PermissionSystem()
        pm = ps.get_permission_manager(OurPost)

        #ipdb.set_trace()
        pm.setup_defaults(blog,u,u)
        perms = ps.get_permissions_for(blog)
        count = 0
        for p in perms : 
            print p
            count=count+1
        self.assertEquals(count,3)

        # in this case, because of the defaults for blog u has access to all interfaces
        blog.load_interfaces_for(u) 
        self.assertEquals(len(blog.get_interfaces()),3)

        u2=User(username='holly')
        u2.save()
        blog2=OurPost(title='test rapping')
        blog2.save()
        blog2=NullInterface(blog2)

        pm.setup_defaults(blog2,u2,u2)

        # in this case, u is only getting access to the Viewer & Commentor interfaces
        blog2.load_interfaces_for(u)
        self.assertEquals(len(blog2.get_interfaces()),2)
        
        
    def testProfile(self) :
        ps = get_permission_system()
        u= User(username='dermot')
        u.save()
        p = u.get_profile()
        p.save()
        for tag in ps.get_permissions_for(p) :
            tag.delete()
        p.save()

        

