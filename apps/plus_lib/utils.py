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


from messages.models import Message
def message_user(sender, recipient, subject, body) :
    m = Message(subject=subject, body=body, sender = sender, recipient=recipient)
    m.save()


from copy import deepcopy
def overlay(d, d2) :
    """ Recursively overlay one dictionary with another
    Rules : if d2 has things not in d, add them
            if d and d2 have value which *isn't* a dictionary, d2 over-rides d
            if d and d2 have item which is a dictionary, 
                        recursively overlay value from d with d2"""
    nd = deepcopy(d)
    for k,v in d2.iteritems() :
        if not nd.has_key(k) :
            nd[k] = v
        elif nd[k].__class__ == dict and d2.__class__ == dict :
            nd[k] = overlay(nd[k],d2[k])
        else :
            nd[k] = d2[k]
    return nd
