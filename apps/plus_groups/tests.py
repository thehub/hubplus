
from apps.hubspace_compatibility.models import TgGroup, Location
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


    def test_make_hub(self) :
        mile_end = Location(name='mile end')
        mile_end.save()
        hub,members,admin = create_hub('mile_end', 'Mile End Hub', location=mile_end, admin=True)
        self.assertEquals(hub.group_name,'mile_end')
        self.assertEquals(hub.display_name,'Mile End Hub')
        self.assertEquals(hub.place,mile_end)
        self.assertEquals(hub.get_extras().group_type,HUB)
        self.assertEquals(hub.get_default_admin(),admin)
        self.assertTrue(members.is_member_of(hub))
        self.assertTrue(admin.is_member_of(hub))


    def test_make_group(self) :
        online = Location(name='online')
        online.save()
        group, admin = create_site_group('greenarchitects', 'Green Architects', location=online)
        self.assertEquals(group.get_extras().group_type,GROUP)
        self.assertEquals(group.group_name,'greenarchitects')
        self.assertEquals(group.get_default_admin(),group)

