
def i_debug(f):
    def g(self):
        try :
            f(self)
        except Exception, e :
            import ipdb
            ipdb.set_trace()
    return g

