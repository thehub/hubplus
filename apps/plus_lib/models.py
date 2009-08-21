
""" This app, plus_lib for common code shared by other hub_plus apps. Might be moved if there's a better place to put it """

class DisplayStatus :
    def __init__(self,txt,time) :
        self.txt=txt
        self.time=time

    def __str__(self) :
        return self.txt


def add_edit_key(cls) :
   def edit_key(self) :
       return '%s-%s-' % (self.__class__.__name__,self.pk)
   cls.edit_key = edit_key


def extract(d,key) :
    if d.has_key(key) :
        v = d[key]
        del d[key]
    else :
        v = None
    return v
