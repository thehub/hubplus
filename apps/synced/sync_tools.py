import settings
import django.dispatch
import threading

tls = threading.local()

class LazyCall(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, *args, **kw):
        self.args = args
        self.kw = kw
    def run(self):
        return self.f(*self.args, **self.kw)

class LazySyncerClient(list):
    def __init__(self, client):
        self._client =client
    def __getattr__(self, name):
        lazy_call = LazyCall(getattr(self._client, name))
        self.append(lazy_call)
        return lazy_call
    def run_all(self):
        self.results = [x.run() for x in self]
        return self.results


def events_setup(syncerclient): 

    class SyncerError(Exception) :
        pass

    def checkSyncerResults(f):
        def wrap(*args, **kw):
            ret = f(*args, **kw)
            f_name = getattr(f, '__name__', str(f))
            if ret:
                t_id, res = ret
                if res and not syncerclient.isSuccessful(res):
                    #raise SyncerError("syncer backend error")
                    return
                if t_id > 0:
                    #tls.syncer_trs.append(t_id)
                    print "syncer_tranaction id: " + `t_id`
                return ret
        return wrap

    # seems like the following isn't relevant to us because we aren't using cherrypy. And doesn't 
    # actually do anything different on either branch of the if. But do we need something similar ? 
    def checkReqHeaders(f):
        def wrap(*args, **kw):
            try:
                if not syncerclient.isSyncerRequest(cherrypy.request.headers.get("user-agent", None)):
                    return f(*args, **kw)
            except AttributeError:
                # outside CheeryPy request which is fine
                    return f(*args, **kw)
        return wrap

    def on_location_add(location=None, **kwargs) :
        print "hubplus sends - on_location_add : %s" % location.name.encode('utf-8')
        xs = tls.syncerclient.onLocationAdd(location.id)
        print xs
        return xs

    def on_location_mod(instance=None, created=None, **kwargs) :
        print "hubplus sends - on_location_mod : %s" % instance.name.encode('utf-8')
        return tls.syncerclient.onLocationMod(instance.id)

    def on_user_add(user=None, **kwargs) :
        print "hubplus sends - on_user_add : %s" % user.username.encode('utf-8')
        return tls.syncerclient.onUserAdd(user.id)
        
    def on_user_mod(user=None, **kwargs) :
        print "hubplus sends - on_user_mod : %s " % user.username.encode('utf-8')
        return  tls.syncerclient.onUserMod(user.id)


    from django.db import transaction

    def synced_transaction(f) :
        @transaction.commit_manually
        def g(*argv,**kwargs) : 
            #tls.syncerclient = LazySyncerClient(syncerclient) 
            try :
                ret = f(*argv,**kwargs)
            except Exception, e:
                transaction.rollback()
                raise e
            
            transaction.commit()
            #tls.syncerclient.run_all() 
            return ret
            # what does this do?
            #if hasattr(tls, 'syncer_trs') and tls.syncer_trs:
            #    syncerclient.completeTransactions(tuple(tls.syncer_trs))
        return g


    return on_user_add, on_user_mod, on_location_add, on_location_mod, synced_transaction


    
        
