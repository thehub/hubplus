import unittest
from models import *
from django.contrib.auth.models import *

class TestStateMachine(unittest.TestCase):
    def test_state_machine(self) :
        sm = StateMachine(
            {0:{'t1':1},
             1:{'t2':2}}
            )
           

        self.assertEquals(sm.count_states(),3)
        self.assertEquals(sm.get_states(),set([0,1,2]))

        self.assertTrue(sm.has_trx('t1'))
        self.assertFalse(sm.has_trx('t3'))
        self.assertEquals(sm.look_up(0,'t1'),1)
        self.assertEquals(sm.look_up(1,'t2'),2)

        self.assertEquals(sm.t1(0),1)
        self.assertEquals(sm.t2(1),2)
        def t1(sm,s) :
            return sm.t1(s)
        self.assertRaises(StateMachineTransitionException,t1,sm,1)


    def test_stored_state_machine(self) :
        sm = StateMachine(
            {0:{'t1':1},
             1:{'t2':2}}
            )

        smr = get_sm_register()
        smr['my_machine']=sm

        u = User(username='state')
        u.save()
        p = u.get_profile()
        p.save()
        u = p.user
      
        ts =TrackedState(machine='my_machine', target=p, state=0)
        ts.save()


        self.assertEquals(TrackedState.objects.filter(target_content_type=ContentType.objects.get_for_model(p), target_object_id=p.id).count(),1)
        ts.next('t1')
        self.assertEquals(ts.state,1)

        ts.next('t2')
        self.assertEquals(ts.state,2)

        def t2(sm,s) :
            return sm.t2(s)
        self.assertRaises(StateMachineTransitionException,t2,sm,ts.state)

        

