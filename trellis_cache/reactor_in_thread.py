from twisted.internet import defer, reactor
import threading
from twisted.python import threadable
from trellis_cache.eventloop import TwistedEventLoop
from mext.context import State
from mext.reaction.eventloop import EventQueue
from mext.reaction.time import Time

__author__ ="Brian Kirsch <bkirsch@osafoundation.org>"

#required for using threads with the Reactor
threadable.init()

class ReactorException(Exception):
      def __init__(self, *args):
            Exception.__init__(self, *args)
            

class TrellisThread(threading.Thread):    
  
      """Run the Reactor in a Thread to prevent blocking the 
         Main Thread once reactor.run is called"""
    
      def __init__(self):
              threading.Thread.__init__(self)
              self._reactorRunning = False
              self.ev_q = None

      def run(self):
              if self._reactorRunning:
                    raise ReactorException("Reactor Already Running")
              
              self._reactorRunning = True
              #call run passing a False flag indicating to the
              #reactor not to install sig handlers since sig handlers
              #only work on the main thread
              self.ev_q = EventQueue.activate()
              Time.activate()
              print "stating reactor"
              TwistedEventLoop.run()
              #reactor.run(False)                
        
      def callInEventLoop(self, callable, *args, **kw):
            #assert self._reactorRunning, ReactorException("Reactor is not running, can't call %s" % `callable`) 
            # heapq is not necessarily thread-safe...I don't know. But "Reaction" transactions are via the GIL and each "EventQueue.call" runs in one
            if self.ev_q is not None:
                  self.ev_q.call(callable, *args, **kw)
            else:
                  while self.ev_q is None:
                        continue
                  self.ev_q.call(callable, *args, **kw)
            #reactor.callFromThread(callable, *args, **kw)
            
      def isReactorRunning(self):
            return self._reactorRunning
       
      def startReactor(self):
            if self._reactorRunning:
                  raise ReactorException("Reactor Already Running")
            threading.Thread.start(self)
            #reactor.addSystemEventTrigger('after', 'shutdown', self.__reactorShutDown)
                        
      def stopReactor(self):
            """may want a way to force thread to join if reactor does not shutdown
               properly. The reactor can get in to a recursive loop condition if reactor.stop 
               placed in the threads join method. This will require further investigation. 
              """
            
            if not self._reactorRunning:
                   raise ReactorException("Reactor Not Running")
            self.ev_q.call(TwistedEventLoop.stop)

            #reactor.callFromThread(reactor.stop)
             
 
      #def addReactorEventTrigger(self, phase, eventType, callable):
      #       if self._reactorRunning:
      #          reactor.callFromThread(reactor.addSystemEventTrigger, phase, eventType, callable)

      #       else:
      #          reactor.addSystemEventTrigger(phase, eventType, callable)
                            
      def __reactorShuttingDown(self):
            pass

      def __reactorShutDown(self):
            """This method called when the reactor is stopped"""
            self._reactorRunning = False
