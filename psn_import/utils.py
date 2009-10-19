from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User
from django.core.files.base import File

import re
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


# Calculate Container
# call get_top_container(uid,[],[])

def get_top_container(uid, path, tags) :

    try :
        g = get_group_for(uid)
        path = [reverse(uid)['title']]+path
        return g
    except Exception, e:
        try :
            u = get_user_for(uid)
            return u
        except :
            dict = reverse[uid]
            if dict.has_key('parentuid') :
                i = dict['parentuid']
                return get_top_container(i)
            elif dict.has_key['mainparentuid'] :
                i = dict['mainparentuid']
                return get_ultimate_container(i)
            else :
                raise Exception("""%s is neither a group or user and has no parentuid or mainparentuid. It's type is a %s""" % (uid,dict['type']))



# Tags
def strip_out(s,bads) :
    return ''.join([c for c in s if (c not in bads)])

from apps.plus_tags.models import tag_add

stop_words = ['of','the','and','in','-']

def tag_words(s) :
    return [strip_out(x.lower(),',') for x in s.split(' ') if (x.lower() not in stop_words)]

def tag_with_folder_name(obj, creator, folder_name, tag_type='folder') :
    for tw in tag_words(folder_name):
        tag_add(obj, tag_type, tw, creator)


# Resources 

from apps.plus_resources.models import get_or_create
from apps.plus_lib.utils import make_name

def psn_group_name(title) :
    # a special group_name maker algorithm for psn
    # compresses MHPSS 
    mhps = 'Mental Health and Psychosocial'
    if mhps in title :
        re.sub(mhps,'mhpss',title)

    r = re.compile('(.*?) Hosts$')
    m = r.match(title)
    if m :
        print s
        host_flag = True
        s = m.group(1) 
    else :
        host_flag = False
    
    s = make_name(title)
    if len(s) > 30 :
        s = s[:30]

    if host_flag :
        s = s + "_hosts"

    return s



def get_creator(dict) :
    return get_user_for(dict['creatoruid'])


def create_resource(top_container, creator, val, f_name, folder) :
    try :
        print "Created by %s" % creator
        title = val.split('.',1)[0]
        name = make_name(title)
        print "Title %s, name %s" % (title,name)
        desc = ''
        license = 'Copyright 2009, Psychosocial Network'
        author = ''
    
        f = File(open('mhpss_export/files/%s'%f_name,'rb'))
    
        resource = get_or_create(creator, top_container,
                             resource=f, title=val, name=name, description=desc,
                             license=license, author=author, stub=False)
        resource.save()
        f.close()
        tag_with_folder_name(resource, creator, folder['title'], 'folder')
        return True
    
    except Exception, e:
        print "******%s",e
        return False
    

def load_all() :
    load_file('folders','mhpss_export/folders.pickle')
    load_file('users','mhpss_export/users.pickle')
    load_file('groups','mhpss_export/groups.pickle')
    load_file('hubs','mhpss_export/hubs.pickle')
    load_file('files','mhpss_export/files.pickle')

