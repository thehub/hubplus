import unittest
import datetime
import simplejson

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.auth.models import User

from apps.hubspace_compatibility.models import TgGroup, Location

from models import *
from apps.plus_groups.models import create_hub, create_site_group

from apps.plus_groups import *

import ipdb

# Permission Management by Content Types
from OurPost import OurPost

#from types import *
  
class TestPermissions(unittest.TestCase):
    def test_generic_reference(self):
        b = OurPost(title="Hello")
        b.save()
        self.assertTrue(b.ref)
        
        b2 = OurPost(title="Hello2")
        b2.save()

        #test explicit security context
        b2.to_security_context()
        sc = b2.get_ref().explicit_scontext
        self.assertEquals(sc.__class__, SecurityContext)
        b.set_security_context(sc)
        self.assertEquals(b2.get_security_context(), b2.get_security_context())

        b3 = OurPost(title="Hello3")
        b3.save()
        b3.acquires_from(b2)
        self.assertEquals(b3.get_security_context(), b2.get_security_context())
