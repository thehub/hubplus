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

        


    def test_content_and_security_context(self) :
        blog = OurPost(title='my post')
        blog.save()

        self.assertTrue(blog.__dict__.has_key('container_object_id'))
        self.assertTrue(blog.__dict__.has_key('security_context_object_id'))

        l = Location(name='HanburyStreet')
        l.save()
        hub,hosts = create_hub(name='hanbury',display_name='Hanbury Street', location=l)

        blog.set_security_context(hub)
        self.assertEquals(blog.security_context,hub)

        blog.set_container(hub)
        self.assertEquals(blog.container,hub)


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
        

        self.assertTrue(ps.has_access(u,blog,tif.get_id(OurPost,'Viewer')))

        t2 = ps.create_security_tag(blog,tif.get_id(OurPost,'Commentor'),[u])

        self.assertTrue(ps.has_access(u,blog,tif.get_id(OurPost,'Commentor')))

        self.assertFalse(ps.has_access(u,blog,tif.get_id(OurPost,'Editor')))


        t3 = ps.create_security_tag(blog2,tif.get_id(OurPost,'Editor'),[editors])
        
        self.assertTrue(ps.has_access(editors,blog2,tif.get_id(OurPost,'Editor')))

        editors.add_member(u)

        self.assertTrue(ps.has_access(u,blog2,tif.get_id(OurPost,'Editor')))
        self.assertFalse(ps.has_access(u,blog,tif.get_id(OurPost,'Editor')))

        self.assertFalse(ps.direct_access(u,blog2,tif.get_id(OurPost,'Editor')))
        self.assertTrue(ps.direct_access(u,blog,tif.get_id(OurPost,'Viewer')))

        t2.delete()
       
        self.assertFalse(ps.has_access(u,blog,tif.get_id(OurPost,'Commentor')))
        ps.delete_access(u,blog,tif.get_id(OurPost,'Viewer'))

        self.assertFalse(ps.has_access(u,blog,ps.get_interface_id(OurPost,'Viewer')))



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
        
        

 

    def XtestSliders(self) :
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
        u = User(username='phil',email_address='phil@the-hub.net')
        u.save()

        # another user (called 'author') who is set as the creator of our blog
        author = User(username='author',email_address='the-hub.net')
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
        
        s = pm.get_interfaces()['Viewer'].make_slider_for(blog,pm.make_slider_options(blog,group,author),u,0,u)

        # now we're just testing that OurPost.Viewer has 5 options for the slider
        self.assertEquals(len(s.get_options()),5)

        # let's see them
        ops = s.get_options()
        self.assertEquals([a.name for a in ops],['World','All Members','Green Architects (owner)','author (creator)','Green Architecture Admin'])

        # and check that it gave us "World" (ie. the everyone group) as the view default. (we assume that blogs default to allowing non members to read them)
        self.assertEquals(s.get_current_option().name,'World')

        tif = ps.get_interface_factory()
        
        self.assertTrue(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Editor')))
        self.assertTrue(ps.has_access(u,blog,tif.get_id(OurPost,'Viewer')))

        # now use the slider to *change* the permission. Behind the scenes this is manipulating SecurityTags.
        s.set_current_option(1) # is it ok to set option using numeric index? Or better with name?
        self.assertEquals(s.get_current_option().name,'All Members')
        self.assertFalse(ps.has_access(everyone,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(all_members,blog,tif.get_id(OurPost,'Viewer')))

        # and again
        s.set_current_option(2) # group level
        self.assertEquals(s.get_current_option().name,'Green Architects (owner)')
        self.assertFalse(ps.has_access(all_members,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(group,blog,tif.get_id(OurPost,'Viewer'))) 

        # and again
        s.set_current_option(3) # author
        self.assertEquals(s.get_current_option().name,'author (creator)')
        self.assertFalse(ps.has_access(group,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(author,blog,tif.get_id(OurPost,'Viewer')))

        # and again
        s.set_current_option(4) # group level
        self.assertEquals(s.get_current_option().name,'Green Architecture Admin')
        self.assertFalse(ps.has_access(author,blog,tif.get_id(OurPost,'Viewer')))
        self.assertTrue(ps.has_access(adminGroup,blog,tif.get_id(OurPost,'Viewer')))



    def XtestProfileSignals(self) :
        from Profile import *
        u = User(username='jesson',email='',password='abc')
        u.save()
        p = u.get_profile()
        p.about='about jesson'
        p.save()
        ps = PermissionSystem()
        self.assertTrue(ps.has_access(ps.get_anon_group(),p,ps.get_interface_factory().get_id(Profile,'Viewer')))


    def XtestUserWrapping(self) :
        u=User(username='oli',email_address='oli@the-hub.net')
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
        for x in perms :
            count=count+1
        self.assertEquals(count,3)

        # in this case, because of the defaults for blog u has access to all interfaces

        ps.get_all_members_group().add_member(u)

        blog.load_interfaces_for(u) 

        self.assertEquals(len(blog.get_interfaces()),3)

        u2=User(username='holly',email_address='holly@the-hub.net')
        u2.save()
        blog2=OurPost(title='test rapping')
        blog2.save()
        blog2=NullInterface(blog2)
        
        pm.setup_defaults(blog2,u2,u2)

        # in this case, u is only getting access to the Viewer & Commentor interfaces
        blog2.load_interfaces_for(u)

        self.assertEquals(len(blog2.get_interfaces()),2)
        

    def testSliderGroup(self) :
        u= User(username='paulo',email_address='paulo@the-hub.net')
        u.display_name=u.username
        u.save()
        
        p = u.get_profile()
        u = p.user
        
        ps = PermissionSystem()


        l = Location(name='biosphere2')
        l.save()

        group = TgGroup(group_name='organiccooks',display_name='Organic Cooks', place=l,created=datetime.date.today())
        group.save()
        #admin_group = TgGroup(group_name='ocadmin', display_name='Organic Cook Admin', place=l,created=datetime.date.today())
        #admin_group.save()
        #da = DefaultAdmin(agent=admin_group,resource=group)
        #da.save()
        blog = OurPost(title='slider testing')
        blog.save()


        pm = ps.get_permission_manager(OurPost)
        pm.setup_defaults(blog,group,u)

        # our permission manager, when it makes the sliders, needs to be able to report the default owner and admins etc.
        self.assertEquals(pm.get_owner(blog,ps.get_interface_id(OurPost,'Viewer')),group)
        self.assertEquals(pm.get_creator(blog,ps.get_interface_id(OurPost,'Viewer')),u)

        group_type = ContentType.objects.get_for_model(ps.get_anon_group()).id
        
        match = simplejson.dumps(
         {'sliders':{
          'title':'title',
          'intro':'intro',
          'resource_id':blog.id,
          'resource_type':ContentType.objects.get_for_model(blog).id, 
          'option_labels':['World','All Members','Organic Cooks (owner)','paulo (creator)' ],
          'option_types':[group_type,group_type,group_type,ContentType.objects.get_for_model(u).id],
          'option_ids':[ps.get_anon_group().id,ps.get_all_members_group().id,group.id,u.id],
          'sliders':['Viewer','Editor'],
          'interface_ids':[ps.get_interface_id(OurPost,'Viewer'),ps.get_interface_id(OurPost,'Editor')],
          'mins':[0,0],
          'constraints':[[0,1]],
          'current':[0,2],
          'extras':{}
          }}
        )

        json = pm.json_slider_group('title','intro',blog,['Viewer','Editor'],[0,0],[[0,1]])

        self.assertEquals(json,match)

        
    def test_agent_constraint(self) :
        # there can only one agent from a collection of options
        # functions to find which option exists and to replace it with another from the set
        ps = get_permission_system()
        u=User(username='hermit',email_address='hermit@the-hub.net')
        u.save()
        b=OurPost(title='post')
        b.save()
        interface=ps.get_interface_id(OurPost,'Viewer')
        anon = ps.get_anon_group()
        all = ps.get_all_members_group()


        def kl(o) : return (ContentType.objects.get_for_model(o).id,o.id)
        
        kill_list = [kl(o) for o in [u, anon, all]]

        s=SecurityTag(name='blaaaah',agent=u,resource=b,interface=interface,creator=u)
        s.save()

        s2=SecurityTag(name='blaah',agent=anon,resource=b,interface=interface,creator=u)
        s2.save()

        u2=User(username='harry',email_address='harry@the-hub.net')
        u2.save()

        s2=SecurityTag(name='aae',agent=u2,resource=b,interface=interface,creator=u)
        s2.save()

        u_type = ContentType.objects.get_for_model(u)
        an_type = ContentType.objects.get_for_model(anon)
        r_type = ContentType.objects.get_for_model(b)

        # check there are three permissions for this
        for x in ps.get_permissions_for(b) : print x
        self.assertEquals(SecurityTag.objects.filter(resource_content_type=r_type,resource_object_id=b.id).count(),3)

        # and then when we kill them, there's only one left
        SecurityTag.objects.kill_list(kill_list,r_type,b.id,interface) 

        for x in ps.get_permissions_for(b) : print x
        self.assertEquals(SecurityTag.objects.filter(resource_content_type=r_type,resource_object_id=b.id).count(),1)

        u3 = User(username='jon',email_address='jon@the-hub.net')
        u3.save()

        s2=SecurityTag(name='bleaaaah',agent=u3,resource=b,interface=interface,creator=u)
        s2.save()
        self.assertTrue(ps.has_access(u3,b,interface))
   
        kill_list = [kl(o) for o in [u3, anon, all]]

        SecurityTag.objects.update(resource=b,interface=interface,new=all,kill=kill_list,name='boo',creator=u)

        self.assertFalse(ps.has_access(u3,b,interface))
        all.add_member(u3)
        self.assertTrue(ps.has_access(u3,b,interface))

        SecurityTag.objects.update(resource=b,interface=interface,new=u3,kill=kill_list,name='boo2',creator=u)
        self.assertTrue(ps.has_access(u3,b,interface))
        self.assertFalse(ps.has_access(all,b,interface))        


    def test_group_admin(self) :
        l = Location(name='Dalston')
        l.save()
        g, h = create_hub(name='hub-dalston',display_name='Hub Dalston', location=l, create_hosts=True)


        
