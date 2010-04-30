
from apps.plus_lib.models import extract
from apps.plus_lib.utils import title_to_name

import unittest

class TestIt(unittest.TestCase) :
    def test(self) :
        class A() :
            def __init__(self,id) :
                self.id = id
        a = A(123)
        from django.conf import settings
        self.assertEquals(cache_key('FROM_OBJ',obj=a), settings.DOMAIN_NAME + ":FROM_OBJ:A:123")
        self.assertEquals(cache_key('FROM_CLASS_AND_ID',cls=A,id=456), settings.DOMAIN_NAME + ":FROM_CLASS_AND_ID:A:456")
        


from apps.plus_lib.redis_lib import cache_key

if __name__ == "__main__":
    unittest.run()
