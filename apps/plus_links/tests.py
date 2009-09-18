
from django.db import models
from django.contrib.auth.models import *

from models import Service, Link, get_links_for, ListOfLinks

from apps.profiles.models import *



import unittest


def count(it) :
    count = 0
    for x in it :
        count=count+1
    return count

from apps.plus_permissions.default_agents import get_admin_user, get_site
from apps.plus_permissions.types.User import create_user

class TestLinks(unittest.TestCase) :

    def make_profile(self,name) :
        u = create_user(name, '%s@x.com'%name)        
        return u, u.get_profile()


    def test_links(self) :
        twitter = Service(name='twitter', url='http://www.twitter.com')
        u,p = self.make_profile('bob')

        link= Link(service=twitter, url='http://www.twitter.com/bob', text='@bob at Twitter', owner=p)
        link.save()

        self.assertEquals(count(get_links_for(p)) ,1)

        link2 = Link(url='http://myblog.blogger.com', text='my blog', owner=p)
        link2.save()
        
        self.assertEquals(count(get_links_for(p)) ,2)

    def xtest_ordered_list(self) :
        
        u,p = self.make_profile('rowena')
        home = Link(url='htp://mysite/com', text='My Site', owner=p)
        flickr = Service(name='Flickr')
        flickr_pics = Link(service=flickr, text='More Photos', url='http://www.flickr.com/ropix', owner=p)
        picassa_pics = Link(text="Photos", url="http://www.picassa.com/ropix", owner=p)

        ll = ListOfLinks([home,flickr_pics,picassa_pics], p)
        self.assertEquals(len(ll), 3)
        self.assertEquals(ll[0], home)

        


