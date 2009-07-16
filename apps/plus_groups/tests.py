
from apps.hubspace_compatibility.models import TgGroup, Location
from models import *
import unittest
import datetime

class TestPlusModels(unittest.TestCase):
    def testExtras(self) :
        l = Location(name='someplace')
        l.save()
        tg = TgGroup(place=l,created=datetime.date.today())
        tg.save()
        extras = GroupExtras(about='this is about my group')
        extras.tg_group = tg
        extras.save()

        self.assertEquals(tg.groupextras,extras)
        self.assertEquals(GroupExtras.objects.get(pk=extras.pk).about,"this is about my group")
        



