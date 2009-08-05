import unittest

from django.db import models
from django.contrib.auth.models import *
from models import *
from profiles.models import *
from plus_groups.models import *
import datetime


        
class TestPsychoSocialCompatibility(unittest.TestCase):

    def testUIDs(self) :
        # for psn compatibility
        u = User(username='alphonso')
        u.save()
        p = u.get_profile()
        p.psn_id='abcdefg'
        p.save()

        p2 = Profile.objects.get(user__user_name='alphonso')
        self.assertEquals(p2.psn_id,'abcdefg')
