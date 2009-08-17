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

from apps.plus_groups import *

from types.OurPost import *

from apps.plus_permissions.api import has_access, has_interfaces_decorator

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
        hubMembers, flag = TgGroup.objects.get_or_create('hub-members',display_name='members', place=l, 
                                                         user=u, level='member')

        # they start with at least two members
        self.assertEquals(hubMembers.get_no_members(),2)

        # we now add member to the group
        hubMembers.add_member(u)
        # which now has one member
        self.assertEquals(hubMembers.get_no_members(),3)
        # and u is a member 
        self.assertTrue(u.is_member_of(hubMembers))
        
        # and hubMembers is itself in u's 'enclosures' (containing groups)
        self.assertTrue(hubMembers in set(u.get_enclosures()))

        # check that you can't add the same member twice
        hubMembers.add_member(u)
        self.assertEquals(hubMembers.get_no_members(),3)

        # another group, called hosts
        hosts,h2 = TgGroup.objects.get_or_create(group_name='admins', display_name='admins', place=l, 
                                                 user=u, level='member')
        hosts.save()

        # u2 is a host
        hosts.add_member(u2)

        # make hosts a member (sub-group) of hubMembers
        hubMembers.add_member(hosts) 
        
        # and check that it's counted as a member
        self.assertEquals(hubMembers.get_no_members(),4)

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

        another_group,created = TgGroup.objects.get_or_create(group_name='site_group',
                                                               display_name='Another Site Group',  
                                                               level='member', user=u)
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

    def test_access(self) :
        """ Starting with security_contexts"""

        nahia = User(username='nahia', email_address='nahia@the-hub.net')
        nahia.save()
        
        adam = User(username='adam', email_address='adam@the-hub.net')
        adam.save()

        kx, kxh = TgGroup.objects.get_or_create(group_name='kingsX', display_name='Hub Kings Cross', level='member', user=adam)
        kxsc = kx.to_security_context()

        blog = kx.create_OurPost(title='my blog')
        blog.save()
        
        # assert that the blog post acquires it's security context from Kings Cross
        self.assertEquals(blog.get_security_context(), kx.get_security_context())

        # confirm that there's an OurPost.Viewer interface for Kings Cross
        self.assertTrue( kx.get_tag_for_interface("OurPost.Viewer"))
                
        i_viewer = get_interface_map(OurPost)['Viewer']

        # but nahia has no access to the blog
        self.assertFalse( has_access(nahia, blog, i_viewer))

        # now lets add this user to the tag
        tag = kx.get_tag_for_interface("OurPost.Viewer")
        tag.add_agents([nahia])

        # so now nahia has access
        self.assertTrue( has_access(nahia, blog, i_viewer))
        
        # but tuba doesn't
        tuba = User(username='tuba', email_address='tuba@the-hub.net')
        tuba.save()

        self.assertFalse( has_access(tuba, blog, i_viewer))

        # however, we presumably want to give kings cross *members* access to it
        tag.add_agents([kx])
        self.assertTrue( has_access(kx, blog, i_viewer))

        # so if we add tuba to kings cross
        kx.add_member(tuba)

        # she now has access
        self.assertTrue( has_access(tuba, blog, i_viewer))
        
        # Now we test that a second blog-post that's created starts with similar access
        blog2 = kx.create_OurPost(title='second post')
        blog2.save()

        self.assertTrue(has_access(tuba, blog2, i_viewer))
        
        # but we assume that not everyone got an editor interface
        i_editor = get_interface_map(OurPost)['Editor']

        self.assertFalse(has_access(tuba, blog2, i_editor))
        
        # so now we're going to give tuba special permissions on this blog post
        # so first make the blog post a custom context
        sc2 = blog2.to_security_context()
        # and make a tag for it
        tag2 = sc2.get_tag_for_interface('OurPost.Editor')
        tag2.add_agent([tuba])
        
        self.assertTrue(has_access(tuba, blog2, i_editor))



        # check that kings cross hosts are a sub-group of kings cross
        self.assertTrue(kxh.is_member_of(kx))

        # so should have same access
        self.assertTrue(has_access(kxh, blog, i_viewer))

        # 



    def test_interfaces(self) :

        u = User(username='deus', email_address='deus@the-hub.net')
        u.save()

        kx, kxh = TgGroup.objects.get_or_create(group_name='kingsX', display_name='Hub Kings Cross', level='member', user=u)
        kxsc = kx.to_security_context()

        blog = kx.create_OurPost(title='another post', body="Here's what")

        caroline = User(username='caroline', email_address='caroline@the-hub.net')
        blog = secure_wrap(blog)

        i_viewer= get_interface_map(OurPost)['Viewer']
        self.assertEquals(i_viewer,OurPostViewer)
        def im(cls, key) :
            return get_interface_map(cls)[key]
        self.assertRaises(Exception,im,OurPost,'xyz')

        blog2 = blog
        
 
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
        
        


    def Xtest_new_slider_set(self) :

        group, TgGroup.objects.get_or_create(group_name='solar cooking', display_name='Solar Chefs', level='member')
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

        u = User(username='God', email_address='god@the-hub.net')
        u.save()

        group, created= TgGroup.objects.get_or_create(group_name='group',
                                                      display_name='Our Group', 
                                                      place=None, level='member', user=u)
        group.to_security_context()

        blog = group.create_OurPost(title='using defaults')

        self.assertEquals(blog.get_security_context().id, group.get_security_context().id)

        blog2 = group.create_OurPost(title='I did it my way')

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

        bsc = b.to_security_context()
        b.set_security_context(b)

        self.assertFalse(has_access(u,b,i_viewer))
        self.assertRaises(PlusPermissionsNoAccessException,foo,FakeRequest(u),b)

        create_security_tag(b,i_viewer,[u])
        self.assertTrue(foo(FakeRequest(u),b))
