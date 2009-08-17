import unittest
import datetime
import simplejson

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User

from apps.hubspace_compatibility.models import TgGroup, Location

from models import *
from interfaces import get_interface_map
import interfaces

from apps.plus_groups.models import create_hub, create_site_group, get_or_create_group
from apps.plus_groups import *

from types.OurPost import *

from apps.plus_permissions.api import create_security_tag, has_access, has_interfaces_decorator

#  


class TestHierarchy(unittest.TestCase):
    def testGroupHierarchy(self):
        # Test the group hierarchies stuff ...

        # make a user
        u = User(username='nils',email_address='nils@the-hub.net')
        u.save()

        # and a couple more
        u2 = User(username='tom',email_address='tom@the-hub.net')
        u2.save()
    
        u3 = User(username='jesson',email_address='jesson@the-hub.net')
        u3.save()

        l = Location(name='kingsX')
        l.save()

        # here's a group (called "hub-members")
        hubMembers, flag = get_or_create_group('hub-members',display_name='members',location=l)

        # they start 
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
        hosts,h2 = create_site_group('admins',display_name='admins',location=l)
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


        another_group,ag_hosts = create_site_group('site_group',display_name='Another Site Group',  create_hosts=True)
        another_group.add_member(hubMembers)
        self.assertTrue(ag_hosts.is_member_of(another_group))
        self.assertFalse(another_group.is_member_of(ag_hosts))


        # Now, if we ask for enclosure_set of u, we should get hubMembers and hosts
        es = u.get_enclosure_set()
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



class TestAccess(unittest.TestCase) :

    def test_permissions(self) :

        u = User(username='synnove',email_address='synnove@the-hub.net')
        u.save()
        
        writers, wh = create_site_group('writers', display_name='writers')
        wsc = writers.to_security_context()
        editors, eh = create_site_group('editors', display_name='editors')

        # two resources, blog and blog2, 
        blog= OurPost(title='my post')    
        blog.save()
  
        # and make writers the acquired security context of the blog
        blog.acquires_from(writers)
    
        i_viewer = get_interface_map(OurPost)['Viewer']
        
        # explicit tag between the writers group, the viewer interface and the user u
        # this means that u has viewer access on writers,
        t = create_security_tag(writers, i_viewer, [u])

        # confirm this
        self.assertTrue(has_access(u, writers, i_viewer))

        # now confirm that u also has access on blog via this security_context
        self.assertTrue(has_access(u, blog, i_viewer))
        
        # confirm that a different user DOESN'T have the same access
        u2 = User(username='joerg', email_address='joerg@the-hub.net')
        u2.save()
        
        self.assertFalse(has_access(writers, blog, i_viewer))
        self.assertFalse(has_access(u2, blog, i_viewer))
        
        # now a second resource, blog2 which is similar to blog1, but we won't give access
        blog2 = OurPost(title='another post')
        blog2.save()

        self.assertFalse(has_access(u,blog2,i_viewer))
        
        # but we'll make it its own security context
        blog2.set_security_context(blog2)
        t2 = create_security_tag(blog2, i_viewer)
        # and we have a tag for it, but no agents associated with the tag
        self.assertFalse(has_access(blog2,i_viewer,u))
        self.assertFalse(has_access(blog2,i_viewer,u2))

        # now we add an agent to a tag
        t2.add_agent(u)
        self.assertTrue(has_access(blog2,i_viewer,u))
        self.assertFalse(has_access(blog2,i_viewer,u2))

        self.assertTrue(ps.has_access(u,blog,i_viewer))

        i_commentor = get_interface_map(OurPost)['Commentor']
        t2 = create_security_tag(blog,i_commentor,[u])

        self.assertTrue(ps.has_access(u,blog,i_commentor))

        ### continue from here 
        i_editor = get_interface_map(OurPost)['Editor']        
        self.assertFalse(ps.has_access(u,blog,i_editor))

        t3 = create_security_tag(blog2,i_editor,[editors])
        
        self.assertTrue(ps.has_access(editors,blog2,i_editor))

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
        discussion_group,discussion_admin = create_site_group('discussion',display_name='Discussion',location=l)
        blog3 = OurPost(title='story')
        blog3.save()

        blog3.set_context(discussion_group)
        blog3.set_security_context(discussion_group)
        
        ps.create_security_tag(discussion_group,IViewer,[u])
        self.assertTrue(ps.has_access(u,blog3,IViewer))
        self.assertFalse(ps.has_access(u,blog3,IEditor))
        
        # and group
        ps.create_security_tag(discussion_group,IEditor,[editors])
        self.assertTrue(ps.has_access(u,blog3,IEditor))
        
                         

    def test_interfaces(self) :

        class A : pass

        force_add()
        self.assertTrue(get_interface_map(OurPost))


        i_viewer= get_interface_map(OurPost)['Viewer']
        self.assertEquals(i_viewer,OurPostViewer)
        def im(cls, key) :
            return get_interface_map(cls)[key]
        self.assertRaises(Exception,im,OurPost,'xyz')

        blog= OurPost(title='what I want to say',body="Here's what")
        blog.save()
        blog2 = blog
        
        blog = secure_wrap(blog,[])
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

        blog.add_interface( get_interface_map(OurPost)['Viewer'])
        self.assertEquals(blog.title,'what I want to say')
        
        def f(blog) : blog.title = "something stupid"
        self.assertRaises(PlusPermissionsReadOnlyException,f,blog)
        
        def try_delete(blog) : 
            blog.delete()
        self.assertRaises(PlusPermissionsNoAccessException,try_delete,blog)

        blog.add_interface( get_interface_map(OurPost)['Editor'])
        
        blog.title = "Hello"
        self.assertEquals(blog.title,'Hello')
        blog.save()

        self.assertEquals(blog2.title,'Hello')

        blog.remove_interface( get_interface_map(OurPost)['Editor'])
        self.assertRaises(PlusPermissionsReadOnlyException,f,blog)
        
        self.assertRaises(PlusPermissionsNoAccessException,try_delete,blog)
        blog.add_interface(get_interface_map(OurPost)['Editor'])

        def foo(r) :
            r.foo()
        self.assertRaises(PlusPermissionsNoAccessException,foo,blog)
        
        class FooRunner(Interface) :
            foo = InterfaceCallProperty('foo')
        
        blog.add_interface(FooRunner)
        blog.foo()

        blog.delete()
        


        

    def test_group_admin(self) :
        l = Location(name='Dalston')
        l.save()
        g, h = create_hub(name='hub-dalston',display_name='Hub Dalston', location=l, create_hosts=True)


    def Xtest_new_slider_set(self) :

        group, hosts = create_site_group('solar cooking', display_name='Solar Chefs', create_hosts=True)
        blog= OurPost(title='parabolic pancakes')
        blog.save()

        # blog belongs to this group's security_context
        blog.set_security_context(group)

        u = User(username='chris',email_address='chris@the_hub.net')
        u.save()
        

        options = [ps.get_anon_group(), ps.get_site_members(), group, hosts]
        
        # slider context is for group
        so = SliderSetObject(group, {'title' : 'My Sliders', 
                           'description' : 'description',
                           'options' : options,
                           'sliders':[ 
                    {
                        'type' : get_interface_map(OurPost)['Viewer'],
                        'title': 'Viewer',
                        'hard_min' : options[0],
                        'soft_min' : options[0],
                        'default' : options[1],
                        'current' : options[1]                 
                    }
                                     ]})
        self.assertEquals(so.context,group)

        self.assertEquals(so.title,'My Sliders')
        self.assertEquals(so.description,'description')
        self.assertEquals(so.options,options)

        
        IViewer = get_interface_map(OurPost)['Viewer']
        slider = so.sliders[0]


        self.assertEquals(slider.type,get_interface_map(OurPost)['Viewer'])
        self.assertEquals(slider.title,'Viewer')
        self.assertEquals(slider.hard_min,options[0])
        self.assertEquals(slider.default,options[1])
        self.assertEquals(slider.current,options[1])
        self.assertEquals(slider.soft_min,options[0])



        # slide up to anybody (remember security_context of sliders are "group")
        so.change_slider(IViewer,ps.get_anon_group())

        # anyone should now have access to blog under IViewer, given that 
        # a) its security_context is group, and b) group has IViewer set to 0 (anybody)
        self.assertTrue(ps.has_access(u,blog,IViewer))

        # now we change through the sliders, by interface and the new setting
        so.change_slider(IViewer,group)
        # and now u lost access
        self.assertFalse(ps.has_access(u,blog,IViewer))

        # but if u joins site_members and the slider is pushed up
        ps.get_site_members().add_member(u)
        so.change_slider(IViewer,ps.get_site_members())
        self.assertTrue(ps.has_access(u,blog,IViewer))

        ss = SliderSet(sliders=so)
        ss.save()

  
class TestSecurityContexts(unittest.TestCase):

    def test_contexts(self) :
        location = Location(name='world')
        location.save()
        group,hosts = create_site_group('group',display_name='Our Group', location=None, create_hosts=True)
        group.to_security_context()

        blog = OurPost(title='using defaults')
        blog.save()
        blog.acquires_from(group)

        self.assertEquals(blog.get_security_context().id, group.get_security_context().id)

        blog2 = OurPost(title='I did it my way')
        blog2.save()
        blog2.acquires_from(group)
        sc2 = blog2.to_security_context()
        blog2.set_security_context(sc2)
        blog2.save()
        self.assertEquals(blog2.get_security_context().id, sc2.id)
        self.assertNotEqual(blog2.get_security_context().id, blog.get_security_context())
        



class TestDecorators(unittest.TestCase) :
    def test_decorators(self) :
        b = OurPost(title='test decorator')
        b.save()

        i_viewer = get_interface_map(OurPost)['Viewer']

        @has_interfaces_decorator(['Viewer'])
        def foo(request, resource, *args, **kwargs) :
            return True

        class FakeRequest :
            def __init__(self, user) :
                self.user = user


        u = User(username='lydia',email_address='tattooed_lady@the-hub.net')
        u.save()

        self.assertFalse(has_access(u,b,i_viewer))

        self.assertRaises(PlusPermissionsNoAccessException,foo,FakeRequest(u),b)

        scb = b.to_security_context()
        create_security_tag(b,i_viewer,[u])
        self.assertTrue(foo(FakeRequest(u),b))
