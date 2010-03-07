from mext.context import State, Service
from mext.reaction import *
from mext.reaction.eventloop import *
from mext.reaction.time import *

from twisted.internet import reactor

__all__ = ['TwistedEventLoop']

if 0:
    class EventQueueSingleton(EventQueue):
        __service__ = EventQueue
        
        @classmethod
        def activate(cls, *args, **kw):
            print "activating"
            if isinstance(EventQueue, EventQueueSingleton):
                r = State[cls.__service__] = State.parent[cls.__service__]
                print "copying"
            else:
                r = State[cls.__service__] = cls(*args, **kw)
                print "new"
            return r

Time.auto_update = True

class TwistedEventLoop(EventLoop):
    """Twisted version of the event loop"""
    __service__ = EventLoop
    _delayed_call = None

    @maintain
    def _ticker(self):
        if self.running:
            print "tick " + `Time.next_event_time`
            next_time = Time.next_event_time
            if next_time is not None:
                self.tick_after(next_time-Time.time)
            if self.stop_requested:
                effect(reactor.stop)

    @effect_method
    def tick_after(self, secs):
        if self._delayed_call and self._delayed_call.active():
            self._delayed_call.reset(secs)
        else:
            print "tick : " + `secs`
            self._delayed_call = reactor.callLater(
                secs, Time.tick
                )

    def _loop(self):
        """Loop updating the time and invoking requested calls"""
        reactor.run(False)

    def _arrange_wakeup(self):
        reactor.callFromThread(lambda:EventQueue.get()._wakeup())
