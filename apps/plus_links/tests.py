
from django.db import models
from django.contrib.auth.models import *

from models import Service, Link, get_links_for, ListOfLinks

from apps.profiles.models import *

from apps.plus_groups.models import make_object_reference, get_referenced_object

import unittest


def count(it) :
    count = 0
    for x in it :
        count=count+1
    return count

class TestLinks(unittest.TestCase) :

    def make_profile(self,name) :
        u = User(username=name)
        u.save()
        p = u.get_profile()
        p.save()
        return u,p

    def test_generic_object_reference(self) :
        u,p = self.make_profile('jen')
        o = make_object_reference(p)
        p2 = get_referenced_object(o.pk)
        self.assertEquals(p.name,p2.name)
        

    def test_links(self) :
        twitter = Service(name='twitter', url='http://www.twitter.com')
        u,p = self.make_profile('bob')

        link= Link(service=twitter, url='http://www.twitter.com/bob', text='@bob at Twitter', owner=p)
        link.save()

        self.assertEquals(count(get_links_for(p)) ,1)

        link2 = Link(url='http://myblog.blogger.com', text='my blog', owner=p)
        link2.save()
        
        self.assertEquals(count(get_links_for(p)) ,2)

    def test_ordered_list(self) :
        
        u,p = self.make_profile('rowena')
        home = Link(url='htp://mysite/com', text='My Site', owner=p)
        flickr = Service(name='Flickr')
        flickr_pics = Link(service=flickr, text='More Photos', url='http://www.flickr.com/ropix', owner=p)
        picassa_pics = Link(text="Photos", url="http://www.picassa.com/ropix", owner=p)

        ll = ListOfLinks([home,flickr_pics,picassa_pics], p)
        self.assertEquals(len(ll), 3)
        self.assertEquals(ll[0], home)

        


