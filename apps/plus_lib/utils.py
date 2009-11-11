from django import forms
import html5lib
from html5lib import sanitizer, serializer, treebuilders, treewalkers


class HTMLField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(HTMLField, self).__init__(*args, **kwargs)

    def clean(self, value):
        chars = super(HTMLField, self).clean(value)
        #chars = chars.encode('utf-8') # should really find out where we have decoded input to unicode and do it there instead
        p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer, tree=treebuilders.getTreeBuilder("dom")) # could use Beautiful Soup here instead
        s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False)
        dom_tree = p.parseFragment(chars) #encoding="utf-8")  - unicode input seems to work fine
        
        walker = treewalkers.getTreeWalker("dom")
        stream = walker(dom_tree)
        gen = s.serialize(stream)
        out = ""
        for i in gen:
            out += i
        return out

class AttrDict(dict):
    """A dict whose items can also be accessed as member variables.

    >>> d = attrdict(a=1, b=2)
    >>> d['c'] = 3
    >>> print d.a, d.b, d.c
    1 2 3
    >>> d.b = 10
    >>> print d['b']
    10

    # but be careful, it's easy to hide methods
    >>> print d.get('c')
    3
    >>> d['get'] = 4
    >>> print d.get('a')
    Traceback (most recent call last):
    TypeError: 'int' object is not callable
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

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
    s=s.strip()
    s=s.replace(' ','_')
    s=s.replace('/','_')
    s=s.replace(',','')
    s=s.lower()
    if isinstance(s,str):
        s = unicode(s,"utf-8")
    return s


from messages.models import Message
def message_user(sender, recipient, subject, body) :
    m = Message(subject=subject, body=body, sender = sender, recipient=recipient)
    m.save()


from django.conf import settings
# XXX : these now moved to the the theme_settings files ... 
# should replace these function calls with the settings constants directly

def hub_name() :
    return settings.HUB_NAME

def hub_name_plural() :
    return settings.HUB_NAME_PLURAL

def main_hub_name() :
    return settings.MAIN_HUB_NAME

def area_from_path(path) :
    # this function takes the path from
    lookup = {'member':'member',
              'group':'group',
              'hub':'hub',
              'region':'hub',
              'explore':'explore',
              'resource':'explore'}

    for k,v in lookup.iteritems() :
        if k in path :
            return v
    return 'unknown'


def search_caption_from_path(path) :
    area = area_from_path(path)
    if area == 'member' :
        caption = settings.MEMBER_SEARCH_TITLE
    elif area == 'group' :
        caption = settings.GROUP_SEARCH_TITLE
    elif area == 'hub' :
        caption = settings.HUB_SEARCH_TITLE
    elif area == 'explore' :
        caption= settings.EXPLORE_SEARCH_TITLE
    else :
        caption = ''
    return caption



