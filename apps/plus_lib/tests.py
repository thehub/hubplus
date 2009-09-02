
from apps.plus_lib.models import extract
from apps.plus_lib.utils import make_name

import unittest

class TestExtract(unittest.TestCase) :

    def test_extract(self) :
        d = {'a':1, 'b':2}
        a = extract(d,'a')
        self.assertEquals(a,1)
        self.assertEquals(d,{'b':2})


    def test_make_name(self):
        self.assertEquals(make_name('hello world'),u'hello_world')
        
