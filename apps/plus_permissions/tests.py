import unittest
import datetime
import simplejson

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User

from apps.hubspace_compatibility.models import TgGroup, Location

from models import *

import interfaces

from apps.plus_groups import *

from OurPost import OurPost

from apps.plus_permissions.api import has_access, has_interfaces_decorator
from apps.plus_permissions.interfaces import secure_wrap, PlusPermissionsNoAccessException, SecureWrapper
from apps.plus_permissions.models import InvalidSliderConfiguration
from apps.plus_permissions.default_agents import get_anonymous_group, get_all_members_group



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

        god = User(username='brahma', email_address='brahma@the-hub.net')
        god.save()

        l = Location(name='kingsX')
        l.save()

        # here's a group (called "hub-members")
        hubMembers, flag = TgGroup.objects.get_or_create('hub-members',display_name='members', place=l, 
                                                         user=god, level='member')

        # they start with at least two members
        self.assertEquals(hubMembers.get_no_members(),2)

        # we now add member to the group
        hubMembers.add_member(u)
        # which now has three members
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
                                                 user=god, level='member')
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

        another_group, created = TgGroup.objects.get_or_create(group_name='site_group',
                                                               display_name='Another Site Group',  
                                                               level='member', user=god)
        another_group.add_member(hubMembers)

        ag_hosts = another_group.get_admin_group() 

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

        kx, created = TgGroup.objects.get_or_create(group_name='kingsX', display_name='Hub Kings Cross', 
                                                level='member', user=adam)
        kxsc = kx.to_security_context()

        blog = kx.create_OurPost(title='my blog', user=adam)
        blog.save()
        
        # assert that the blog post acquires it's security context from Kings Cross
        self.assertEquals(blog.get_inner().get_security_context().id, kx.get_security_context().id)

        # confirm that there's an OurPost.Viewer interface for Kings Cross
        self.assertTrue( kx.get_tag_for_interface("OurPost.Viewer"))
                
        # but nahia has no access to the blog
        self.assertFalse(has_access(nahia, blog, "OurPost.Viewer"))

        # now lets add this user to the tag
        tag = kx.get_tag_for_interface("OurPost.Viewer")
        tag.add_agents([nahia.get_ref()])

        # so now nahia has access
        self.assertTrue( has_access(nahia, blog, "OurPost.Viewer"))
        
        # but tuba doesn't
        tuba = User(username='tuba', email_address='tuba@the-hub.net')
        tuba.save()

        self.assertFalse( has_access(tuba, blog, "OurPost.Viewer"))

        # however, we presumably want to give kings cross *members* access to it
        tag.add_agents([kx.get_ref()])
        self.assertTrue( has_access(kx, blog, "OurPost.Viewer"))

        # so if we add tuba to kings cross
        kx.add_member(tuba)

        # she now has access
        self.assertTrue( has_access(tuba, blog, "OurPost.Viewer"))
        
        # Now we test that a second blog-post that's created starts with similar access
        blog2 = kx.create_OurPost(user=adam, title='second post')
        blog2.save()

        self.assertTrue(has_access(tuba, blog2, "OurPost.Viewer"))
        
        # but we assume that not everyone got an editor interface

        self.assertFalse(has_access(tuba, blog2, "OurPost.Editor"))
        
        # add an arbitrary agent and remove her agaiin 
        blog._inner.get_security_context().add_arbitrary_agent(tuba, 'OurPost.Editor', adam)
        self.assertTrue(has_access(tuba, blog, "OurPost.Editor"))
        blog._inner.get_security_context().remove_arbitrary_agent(tuba, 'OurPost.Editor', adam)
        self.assertFalse(has_access(tuba, blog, "OurPost.Editor"))        

        #test moving the sliders around
        members_group = blog._inner.get_security_context().context_agent.obj
        admin_group = blog._inner.get_security_context().context_admin.obj
        
        #set the slider so that members of KX have the Editor interface
        blog._inner.get_security_context().move_slider(members_group, 'OurPost.Editor', adam)

        #check that the slider level actually changed
        level = blog._inner.get_security_context().get_slider_level('OurPost.Editor')
        self.assertTrue(level==members_group)

        #and check that tuba has access
        self.assertTrue(has_access(tuba, blog, "OurPost.Editor"))

        #now remove tuba from the members group
        members_group.remove_member(tuba)
        self.assertFalse(has_access(tuba, blog, "OurPost.Editor"))        

        #and re-add her
        members_group.add_member(tuba)
        self.assertTrue(has_access(tuba, blog, "OurPost.Editor"))  

        #raise the requirement to the admin group
        blog.get_inner().get_security_context().move_slider(admin_group, 'OurPost.Editor', adam)
        level = blog.get_inner().get_security_context().get_slider_level('OurPost.Editor')

        #check the slider changed and that adam can now access while tuba cannot
        self.assertTrue(level==admin_group)
        self.assertFalse(has_access(tuba, blog, "OurPost.Editor"))
        self.assertTrue(has_access(adam, blog, "OurPost.Editor"))

        #use the move_sliders interface which should be called by the UI and check that constraints are enforced correctly
         # this should fail validation  because editor can't be higher than viewer
        def move_sliders(slider_dict, type_name, user):
            blog._inner.get_security_context().move_sliders(slider_dict, type_name, user=user)
        anonymous_group = get_anonymous_group()
        self.assertRaises(InvalidSliderConfiguration, move_sliders, {'OurPost.Editor':members_group, 'OurPost.Viewer':admin_group},  'OurPost', adam)
         # so should this because Editor can't be anonymous
        self.assertRaises(InvalidSliderConfiguration, move_sliders, {'OurPost.Editor':anonymous_group, 'OurPost.Viewer':anonymous_group},  'OurPost', adam)
         # check that nothing changed
        level = blog._inner.get_security_context().get_slider_level('OurPost.Editor')
        self.assertTrue(level==admin_group)
        
         # this should validate        
        blog._inner.get_security_context().move_sliders({'OurPost.Editor':members_group, 'OurPost.Viewer':members_group}, 'OurPost', adam)
        # and levels should be changed
        level = blog._inner.get_security_context().get_slider_level('OurPost.Editor')
        self.assertTrue(level==members_group)
        level = blog._inner.get_security_context().get_slider_level('OurPost.Viewer')
        self.assertTrue(level==members_group)

        
        # so now we're going to give tuba special permissions on this blog post ONLY
        # so first make the blog post a custom context
        sc2 = blog2.create_custom_security_context()

        # assert now that blog2's security context is NOT the same as blog's
        self.assertNotEquals(blog2._inner.get_security_context(), blog._inner.get_security_context())
        # but that the admin and agent are
        self.assertEquals(blog2._inner.get_security_context().get_context_agent(), blog._inner.get_security_context().get_context_agent())
        self.assertEquals(blog2._inner.get_security_context().get_context_admin(), blog._inner.get_security_context().get_context_admin())

        # another kings cross host
        elenor = User(username='elenor', email_address='elenor@the-hub.net')
        elenor.save()
        
        # who doesn't have access
        self.assertFalse(has_access(elenor, blog2, 'OurPost.Editor'))
        
        # so we add her to the tag
        sc2.add_arbitrary_agent(elenor, 'OurPost.Editor', adam)
        
        # and she now has access
        self.assertTrue(has_access(elenor, blog2, "OurPost.Editor"))

        # let's take her away again and check she loses access
        blog2.remove_arbitrary_agent(elenor, 'OurPost.Editor', adam)
        self.assertFalse(has_access(elenor, blog2, "OurPost.Editor"))

        # and if we add elinor to kx
        kx.add_member(elenor)
        
        # so should have same access
        self.assertTrue(has_access(elenor, blog, "OurPost.Editor"))   
                       



    def test_interfaces(self) :
        
        u = User(username='deus', email_address='deus@the-hub.net')
        u.save()

        phil = User(username='phil', email_address='phil.jones@the-hub.net')
        phil.save()

        kx, created = TgGroup.objects.get_or_create(group_name='kingsX', display_name='Hub Kings Cross', level='member', user=u)
       
        caroline = User(username='caroline', email_address='caroline@the-hub.net')
        caroline.save()
        all_members = get_all_members_group()
        all_members.add_member(caroline)

        carolines_kx_secure = secure_wrap(kx, caroline)
        #since caroline is only a site members she should be able to get the Viewer interface on TgGroup and OurPost, and Join TgGroup, but nothing else.
        carolines_kx_secure.about
        carolines_kx_secure.place
        carolines_kx_secure.join

        #
        def try_create_post(secure_kx):
            return secure_kx.create_OurPost(title='another post', body="Here's what", user=caroline)
        self.assertRaises(PlusPermissionsNoAccessException, try_create_post, carolines_kx_secure)

        def view_attribute(sec_object, attr_name):
            getattr(carolines_kx_secure, attr_name)
        def edit_attribute(sec_object, attr_name, val):
            setattr(carolines_kx_secure, attr_name, val)

        self.assertRaises(PlusPermissionsReadOnlyException, edit_attribute, carolines_kx_secure, 'about', "Bernhard Lietar's Future of Money")
        self.assertRaises(PlusPermissionsNoAccessException, view_attribute, carolines_kx_secure, 'invite_member')
        kx.add_member(caroline)
        #now caroline can now also add blog posts to KX secure 
        carolines_kx_secure = secure_wrap(kx, caroline)
        blog = try_create_post(carolines_kx_secure)
        self.assertEquals(blog.__class__, SecureWrapper)
        
        blog.title = "blah"
        blog.body = "test"
        self.assertEquals(blog.title, "blah")
        self.assertEquals(blog.body, "test")
        
        phils_blog_secure = secure_wrap(blog, phil)
        self.assertRaises(PlusPermissionsReadOnlyException, edit_attribute, phils_blog_secure, "title", "Phils Blog")

        self.assertRaises(PlusPermissionsReadOnlyException, edit_attribute, carolines_kx_secure, "about", "Bernhard Lietar's Future of Money")
        kx.get_admin_group().add_member(caroline)
        carolines_kx_secure = secure_wrap(kx, caroline)        
        carolines_kx_secure.about = "Bernhard Lietar's Future of Money"

  
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
        group.add_member(u)
        blog = group.create_OurPost(title='using defaults', user=u)
        
        self.assertEquals(blog.get_inner().get_security_context().id, group.get_security_context().id)

        blog2 = group.create_OurPost(title='I did it my way', user=u)

        sc2 = blog2.get_inner().to_security_context()
        blog2.get_inner().set_security_context(sc2)
        blog2.save()
        self.assertEquals(blog2.get_inner().get_security_context().id, sc2.id)
        self.assertNotEqual(blog2.get_inner().get_security_context().id, blog.get_inner().get_security_context().id)
        

class TestDecorators(unittest.TestCase) :
    def test_decorators(self) :

        god = User(username='Jupiter', email_address='jupiter@the-hub.net')
        god.save()

        group, created= TgGroup.objects.get_or_create(group_name='group',
                                                      display_name='Our Group', 
                                                      place=None, level='member', user=god)
        group.to_security_context()

        b = group.create_OurPost(god, title='test decorator')
        from apps.plus_permissions.models import get_interface_map
        i_editor = get_interface_map(OurPost)['Editor']

        @has_interfaces_decorator(OurPost, ['Editor'])
        def foo(request, resource, *args, **kwargs) :
            resource.title = "blah"
            return True

        class FakeRequest :
            def __init__(self, user) :
                self.user = user

        u = User(username='lydia',email_address='tattooed_lady@the-hub.net')
        u.save()

        self.assertFalse(has_access(u, b, 'OurPost.Editor'))


        self.assertRaises(PlusPermissionsReadOnlyException, foo, FakeRequest(u), b.id)

        b.get_inner().get_security_context().add_arbitrary_agent(u, 'OurPost.Editor', god)
        self.assertTrue(foo(FakeRequest(u), b.id))

    def test_custom_managers(self) :
        # confirm we really customized them
        self.assertTrue(TgGroup.objects.is_custom())
        self.assertTrue(User.objects.is_custom())
        
        import ipdb
        #ipdb.set_trace()

        god = User(username='Loki', email_address='loki@the-hub.net')
        god.save()

        group, created= TgGroup.objects.get_or_create(group_name='lokusts',
                                                      display_name="Loki's Group", 
                                                      place=None, level='member', user=god)

        blog1 = group.create_OurPost(user=god, title='post1', body='X')
        blog2 = group.create_OurPost(user=god, title='post2', body='X')
        blog3 = group.create_OurPost(user=god, title='post3', body='X')

        manfred = User(username='manfred', email_address='manfred@the-hub.net')
        manfred.save()

        self.assertEquals(OurPost.objects.plus_count(manfred, body='X'),0)
        
        sc2 = blog2.create_custom_security_context()
        sc2.add_arbitrary_agent(manfred, 'OurPost.Viewer', god)


        self.assertEquals(OurPost.objects.plus_count(manfred, body='X'), 1)
        p = OurPost.objects.plus_get(manfred, title='post2')

        self.assertEquals(p.__class__, SecurityWrapper)

        def f(p) :
            p.set_title('other')

        self.assertRaises(PlusPermissionsNoAccessException, f, p)



