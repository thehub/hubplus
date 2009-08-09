from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class StateMachineTransitionException(Exception) : pass

class StateMachine :
    def __init__(self,dict):
        self.table = dict
        self.states = set(dict.keys())

        self.inverted = {}
        
        for state, trans in self.__dict__['table'].iteritems() :
            for t,v in trans.iteritems() :
                self.__dict__['states'].add(v)
                if not self.__dict__['inverted'].has_key(t) :
                    self.__dict__['inverted'][t] = {}
                self.__dict__['inverted'][t]={state:v}

        for tfr, map in self.__dict__['inverted'].iteritems() :
            setattr(self,tfr,self.make_func(map,))

    def make_func(self,map) :
        def f(x) :
            try :
                return map[x]
            except :
                raise StateMachineTransitionException("Transition doesn't exist")

        return f

    def has_trx(self,name) :
        for state, trans in self.__dict__['table'].iteritems() :
            if trans.has_key(name) : 
                return True

        return False

    def look_up(self,s1,trx) :
        return self.__dict__['table'][s1][trx]
    
            
    def get_states(self) :
        return self.__dict__['states']

    def count_states(self) :
        return len(self.get_states()) 


    
_STATE_MACHINE_REGISTER={}

def get_sm_register() :
    return _STATE_MACHINE_REGISTER



class TrackedState(models.Model) :
    ''' Tracking which state in a state-machine a resource is at'''

    machine = models.CharField(max_length=30)
    state = models.CharField(max_length=30)

    target_content_type = models.ForeignKey(ContentType,related_name='state_machine_target')
    target_object_id = models.PositiveIntegerField(null=True)
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')

    def next(self,trx) :
        self.state = get_sm_register()[self.machine].look_up(self.state,trx)
        self.save()


    

