
from apps.plus_lib.models import extract

import unittest

class TestExtract(unittest.TestCase) :

    def test_extract(self) :
        d = {'a':1, 'b':2}
        a = extract(d,'a')
        self.assertEquals(a,1)
        self.assertEquals(d,{'b':2})
