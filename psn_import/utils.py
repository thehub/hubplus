from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User

import pickle

maps = {}
reverse = {}

def load_file(type,f_name) :
    xs = pickle.load(open(f_name))
    maps[type] = xs
    for x in xs :
        reverse[x['uid']] = (type,x)


def list_type(type,fields) :
    if 'all' in fields :
        print maps[type][0].keys()
    for x in maps[type] :
        for f in fields :
            if f != 'all' :
                try:
                    print x[f]+' ',
                except :
                    print "<<failed to print a %s>> " % f,
        print


def get_for(uid) :
    if reverse.has_key(uid) :
        return reverse[uid]
    else :
        raise Exception("Nothing seems to have %s " %uid)
        
def get_obj_for(cls, uid) :
    xs = cls.objects.filter(psn_id=uid)
    if xs.count() > 0 :
        return xs[0]
    raise Exception('not found')

def get_group_for(uid) :
    return get_obj_for(TgGroup,uid)

def get_user_for(uid):
    return get_obj_for(User,uid)
