from django.conf import settings

from redis import Redis
redis = Redis()

CACHE_ON = True

def cache_key(prefix, obj=None, cls='', id='' ) :
    if obj :
        return "%s:%s:%s:%s" %(settings.DOMAIN_NAME, prefix, obj.__class__.__name__, obj.id)
    else :
        return "%s:%s:%s:%s" %(settings.DOMAIN_NAME, prefix, cls.__name__, id)

def add_to_cached_set(key, xs) :
    pipe = redis.pipeline()
    for x in xs :
        pipe.sadd(key, x)

    if CACHE_ON :
        pipe.execute()



# decorator to invalidate cache
def invalidates_cache_for(keyword) :
    def inner(f) :
        def _cache_invalidator(self, *args,**kwargs) :
            key = cache_key(self,keyword)
            redis.delete(key)
            return f(self, *args, **kwargs)

        return _cache_invalidator
    return inner


def walk_children(obj, f, seen=None, path='', **kwargs) :
    """ Recurses through all members and calls f on them"""
    if seen == None :
        seen = set([obj])
    else :
        if obj in seen :
            return

    f(obj, **kwargs)
    seen.add(obj)
    if getattr(obj,'get_members',False) :
        for child in obj.get_members() :
            if not child in seen :
                walk_children(child, f, seen, path=path+'/%s'%obj, **kwargs)

ONE_LEVEL_MEMBERSHIP_KEY = "membership_ids"
MULTI_LEVEL_MEMBERSHIP_KEY = "multi_membership_ids"

def invalidates_membership_cache(f) :
    """ decorator for functions that should invalidate the membership cache"""
    def _invalidate_membership_cache_closure(self, *args, **kwargs) :
        """ kills the membership cache and then calls f"""
        def kill_membership_cache(obj) :
            """ kills the cached membership information for obj"""
            key = cache_key(ONE_LEVEL_MEMBERSHIP_KEY, obj=obj)
            redis.delete(key)
            key = cache_key(MULTI_LEVEL_MEMBERSHIP_KEY, obj=obj)
            redis.delete(key)
        walk_children(self, kill_membership_cache)

        return f(self,*args,**kwargs)
    return _invalidate_membership_cache_closure


def cached_for(obj) :
    d = {}
    def add(prefix) :
        key = cache_key(prefix,obj)
        if redis.exists(key) :
            d[prefix]=redis.smembers(key)
    
    add(ONE_LEVEL_MEMBERSHIP_KEY)
    add(MULTI_LEVEL_MEMBERSHIP_KEY)

    return d

    

                        
