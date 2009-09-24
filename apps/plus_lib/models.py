
""" This app, plus_lib for common code shared by other hub_plus apps. Might be moved if there's a better place to put it """

class DisplayStatus :
    def __init__(self,txt,time) :
        self.txt=txt
        self.time=time

    def __str__(self) :
        return self.txt

from apps.plus_user.models import User

def add_edit_key(cls) :
    def edit_key(self) :
        if self.__class__ == User:
            id = self.username
        else:
            id = self.pk
        return '%s-%s-' % (self.__class__.__name__, id)
    cls.edit_key = edit_key

def add_get_display_name(cls) :
    # using get_display_name rather than display name because some model classes already have attributes called 
    # display_name and we don't want to hide it 
    def get_display_name(self) :
        try : 
            self.first_name
            self.last_name
            if self.first_name and self.last_name :
                return '%s %s' % (self.first_name, self.last_name)
        except :
            pass
        
        try :
            if self.display_name :
                return self.display_name
        except :
            pass
 
        try :
            if self.name :
                return self.name
        except :
            pass
        
        try:
            if self.group_name :
                return self.group_name
        except :
            pass

        if self.__class__.__name__ == 'User' :
            try :
                return self.get_profile().get_display_name()
            except :
                # may fail if we're still setting up the user
                pass

        return '(class: %s, pk: %s)' % (self.__class__.__name__, self.pk)

    cls.get_display_name = get_display_name


def extract(d,key) :
    if d.has_key(key) :
        v = d[key]
        del d[key]
    else :
        v = None
    return v


def make_user(name, password, email_address) :
    from django.contrib.auth.models import User

    u = User(username=name, email_address=email_address)
    u.save()
    u.set_password(password)
    
