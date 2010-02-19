
from django.conf import settings
from django.http import HttpResponse
import settings
import django.dispatch


from models import get_sessions

# Sets up custom signals for events which are interesting to syncer
post_user_create = django.dispatch.Signal(providing_args=['user'])
post_user_mod = django.dispatch.Signal(providing_args=['user'])
post_location_add = django.dispatch.Signal(providing_args=['location'])


if not settings.SYNC_ENABLED:
    def synced_transaction(f) :
        """ Need this because if the SYNC_ENABLED flag isn't set, we won't have the real synced_transaction
        but it's refered to in other apps."""
        def g(*args,**kwargs) :
            return f(*args,**kwargs)
        return g
else:
    from apps.account.views import login
    import thread
    import time
    import cookielib

    real_login = login
    import syncer.client
    import syncer.config
    import syncer.utils

    from sync_tools import LazySyncerClient

    syncer.config.host = settings.SYNCER_HOST
    syncer.config.port = settings.SYNCER_PORT
    syncer.config.reload()


    from apps.synced.models import get_sessions
    sessiongetter = lambda : get_sessions()

    # _sessions = {}
    # sessiongetter = lambda: _sessions

    syncerclient = syncer.client.SyncerClient("hubplus", sessiongetter)

    def login(*args, **kw):
        print "________starting login (%s,%s)" % (thread.get_ident(), id(syncerclient.sessiongetter()))
        print syncerclient.sessiongetter()

        request = args[0]
        req_cookies = request.COOKIES
        u = request.POST.get('username')
        p = request.POST.get('password')
        resp = real_login(*args, **kw)
        # good ref: http://docs.djangoproject.com/en/dev/ref/request-response/
        if not syncerclient.isSyncerRequest(request.META['HTTP_USER_AGENT']) and resp.status_code == 302:
            cl = [ cookielib.Cookie(None, name, value, None, None, settings.SESSION_COOKIE_DOMAIN, None, None, '/', None, "", None, "", "", None, None)
                for (name, value) in req_cookies.items() ]
 
            print "syncertoken " + `syncerclient.getSyncerToken()`
            print "thread id is "+`thread.get_ident()`
            tr_id, res = syncerclient.onUserLogin(u, p, cl)
            print ".....",res

            if not syncerclient.isSuccessful(res):
                print syncer.client.errors.res2errstr(res)
            else:
                for v in res.values():
                    try:
                        sso_cookies = v['result']
                        for c in sso_cookies:
                            resp.set_cookie(c.name, value=c.value, max_age=None, path=c.path, domain=settings.SESSION_COOKIE_DOMAIN, secure=c.secure)
                    except Exception, err:
                            print "SSO: skipping ", v['appname']

        return resp

    def signon():

        u = settings.HUBPLUSSVCUID
        p = settings.HUBPLUSSVCPASS
        tr_id, res = syncerclient.onSignon(u, p)
        if syncerclient.isSuccessful(res):
            print "setting syncer token (%s, %s)" % (`thread.get_ident()`,`id(syncerclient.sessiongetter())`)
            print syncerclient.sessiongetter()
            syncerclient.setSyncerToken(res['sessionkeeper']['result'])
            print syncerclient.sessiongetter()
            print "syncertoken " + `syncerclient.getSyncerToken()`
            msg = "Syncer signon successful"
            print msg

            return True
        msg = "Syncer signon failed: %s" % res
        print msg
        msg = syncer.client.errors.res2errstr(res)
        print msg

   
    def signonloop():
        while not signon():
            time.sleep(10)

    thread.start_new(signonloop, ())

    # get the events functions
    from sync_tools import events_setup 

    on_user_add, on_user_mod, on_location_add, on_location_mod, _synced_transaction = events_setup(syncerclient)

    post_user_create.connect(on_user_add)
    post_user_mod.connect(on_user_mod)
    post_location_add.connect(on_location_add)

    synced_transaction = _synced_transaction
