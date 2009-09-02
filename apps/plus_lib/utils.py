
def i_debug(f):
    def g(*args, **kwargs):
        try :
            f(*args,**kwargs)
        except Exception, e :
            import ipdb
            ipdb.set_trace()
    return g



def make_name(s):
    """Turn the argument into a name suitable for a URL """
    s=s.replace(' ','_')
    if isinstance(s,str):
        s = unicode(s,"utf-8")
    return s
