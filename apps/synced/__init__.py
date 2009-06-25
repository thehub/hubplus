from account.views import login
from django.conf import settings
from django.http import HttpResponse
import settings

if settings.SYNC_ENABLED:
    import thread
    import time
    import cookielib

    real_login = login
    import syncer.client
    import syncer.config
    import syncer.utils

    syncer.config.host = settings.SYNCER_HOST
    syncer.config.port = settings.SYNCER_PORT
    syncer.config.reload()

    _sessions = dict()
    sessiongetter = lambda: _sessions
    syncerclient = syncer.client.SyncerClient("hubplus", sessiongetter)

    def sso(u, p):
        ret = syncerclient.onUserLogin(u, p)
        tr_id, res = ret
        cookies = []
        if 'authcookies' in res:
            for appname in res['authcookies']:
                for c in res['authcookies'][appname]:
                    cookies.append(c)
        if not syncerclient.isSuccessful(res):
            print syncer.client.errors.res2errstr(res)
            # warning
        return cookies

    def login(*args, **kw):
        request = args[0]
        req_cookies = request.COOKIES
        u = request.POST.get('username')
        p = request.POST.get('password')
        resp = real_login(*args, **kw)
        # good ref: http://docs.djangoproject.com/en/dev/ref/request-response/
        if not syncerclient.isSyncerRequest(request.META['HTTP_USER_AGENT']) and resp.status_code == 302:
            cl = [ cookielib.Cookie(None, name, value, None, None, settings.SESSION_COOKIE_DOMAIN, None, None, '/', None, "", None, "", "", None, None)
                for (name, value) in req_cookies.items() ]
            tr_id, res = syncerclient.onUserLogin(u, p, cl)
            if not syncerclient.isSuccessful(res):
                print syncer.client.errors.res2errstr(res)
            else:
                for v in res.values():
                    sso_cookies = v['result']
                    for c in sso_cookies:
                        resp.set_cookie(c.name, value=c.value, max_age=None, path=c.path, domain=settings.SESSION_COOKIE_DOMAIN, secure=c.secure)


        return resp

    def signon():
        u = settings.HUBPLUSSVCUID
        p = settings.HUBPLUSSVCPASS
        tr_id, res = syncerclient.onSignon(u, p)
        if syncerclient.isSuccessful(res):
            syncerclient.setSyncerToken(res['sessionkeeper']['result'])
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
