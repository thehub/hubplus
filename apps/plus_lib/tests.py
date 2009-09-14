
from apps.plus_lib.models import extract
from apps.plus_lib.utils import make_name, overlay

import unittest

class TestExtract(unittest.TestCase) :

    def test_extract(self) :
        d = {'a':1, 'b':2}
        a = extract(d,'a')
        self.assertEquals(a,1)
        self.assertEquals(d,{'b':2})


    def test_make_name(self):
        self.assertEquals(make_name('hello world'),u'hello_world')
        

    def test_overlay(self) :
        d = {}
        d2 = overlay(d, {'a':1}) 
        self.assertEquals(d2,{'a':1})

        d = {'a':1, 'b':{'c':2}, 'd':[1,2,3] }
        d2 = overlay(d,{'a':11, 'b': {'c2':3}})
        self.assertEquals(d2,{'a':11,'b':{'c':2,'c2':3},'d':[1,2,3]})
        
        d = {'a':{'b':{'c':2}}}
        d2 = {'a':{'b':{'c':3}}}
        d2 = overlay(d, d2)
        self.assertEquals(d2['a']['b']['c'],3)


