from hashlib import sha1
import hmac as create_hmac
from django.conf import settings
from django.contrib.auth.models import User

def attach_hmac(url, proxy):
    #proxy should be taken directly from request.user here

    if url.find('=') > 0 :
        url += '&'
    else :
        url += '?'
    url += "proxy=%s" %proxy

    hmd = create_hmac.new(settings.HMAC_KEY, url, sha1).hexdigest()
    print "A %s, %s" % (hmd, url)

    url += "&hmac=%s" %hmd
    return url

def confirm_hmac(request):
    url = request.get_full_path()
    url, auth_code = url.split("&hmac=")
    hmd = create_hmac.new(settings.HMAC_KEY, url, sha1).hexdigest()
    print "B %s, %s" % (hmd, url)

    if hmd == auth_code and "proxy=" in url:
       user = User.objects.get(username=request.GET.get("proxy"))       
       return (True, user)
    return False, None

class BadProxyUserException(Exception):
    def __init__(self, msg, proxy=None, url=None) :
        self.proxy = proxy
        self.url = url
        self.msg = msg

def hmac_proxy(f) :
    def g(request, *args, **kwargs) :
        path = request.get_full_path()
        if path.find('hmac') > 0 :
            confirmed, agent = confirm_hmac(request)
            if not confirmed :
                print "BadProxyUserException %s, %s, %s"%(confirmed, agent, path)
                raise BadProxyUserException("agent %s isn't confirmed by the hmac code" % request.GET['proxy'],
                                            request.GET['proxy'], path)
            else :
                request.old_user = request.user
                request.user = agent
        return f(request, *args, **kwargs)
    return g

            
