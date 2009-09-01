
from apps.plus_groups.models import TgGroup, Location
from models import *

import unittest
import datetime
        
class TestPlusModels(unittest.TestCase):


        

   
    def field(self,extras,name,val) :
        setattr(extras,name,val)
        extras.save()
        e2 = GroupExtras.objects.get(pk=extras.pk)
        self.assertEquals(getattr(e2,name),val)
                  
        
    def testExtras(self) :
        l = Location(name='someplace')
        l.save()
        tg = TgGroup(place=l,created=datetime.date.today())
        tg.save()
        extras = GroupExtras(about='this is about my group')
        extras.tg_group = tg

        self.assertEquals(tg.groupextras,extras)

        extras.save()
        e2 = GroupExtras.objects.get(pk=extras.pk)

        self.field(extras,'path','abc')
        self.field(extras,'title','abc')
        self.field(extras,'description','abc')
        self.field(extras,'body','abc')
        self.field(extras,'rights','abc')
        self.field(extras,'psn_id','abc')
        self.field(extras,'path','abcd')

        self.field(extras,'psn_id','abc')

        self.assertEquals(e2.about,"this is about my group")





    

