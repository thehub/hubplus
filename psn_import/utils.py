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
    # list some fields from a particular type
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
 
    if reverse.has_key(uid) :
        e = entity(uid)
        et = e_type(uid)
        if et == 'Group' or et == 'Hub' :
            gs = TgGroup.objects.filter(psn_id=uid)
            if gs :
                return gs[0]
            else :
                print "%s seems to be a group but wasn't created as a TgGroup" % uid.encode('utf-8')
                ipdb.set_trace()
                return None

        elif et == 'User' :
            us = User.objects.filter(username=e['username'])
            if us :
                u = us[0]
                tag_s = tag_words(u.get_display_name())
                tag_s.append(u.username)
                for tw in tag_s :
                    tags.append(tw)
                return u
            else :
                print "%s seems to be a user, but we don't have in Users"
                ipdb.set_trace()
                return None
            
        else :
            typ, dict = reverse[uid]
            if dict.has_key('parentuid') :
                
                i = dict['parentuid']
                path.append(title(uid))
                tag_s = tag_words(title(uid))
                for tw in tag_s :
                    tags.append(tw)
                return get_top_container(i,path,tags)
            elif dict.has_key('mainparentuid'):
                i = dict['mainparentuid']
                path.append(title(uid))
                tag_s = tag_words(title(uid))
                for tw in tag_s :
                    tags.append(tw)
                return get_ultimate_container(i,path,tags)
            else :
                print dict
                
                ipdb.set_trace()
    else :
        raise Exception("""We don't know about %s which is neither a group or user and has no parentuid or mainparentuid. It's type is a %s""" % (uid,e_type(uid)))



# Tags
def strip_out(s,bads="""/,"':()[]*\%\\?;""") :
    return ''.join([c for c in s if (c not in bads)])


from apps.plus_tags.models import tag_add

stop_words = ['of','the','and','in','-','a','at','for','&','after','le','la','dans','les','with','to','de','against','all','or','set','up','lets','are','from','','1', '2', '3 - 30' , 'about', 'info', 'advisory', 'including', 'inform', 'global', 'materials', 'seminars']

substitutes = {
  'set' : 'setup',
}

def flatten(build,s,sep) :
    reg = re.compile('[%s]'%sep)
    if not reg.search(s) :
        build.add(s)
    else :
        for p in reg.split(s) :
            build.add(p)

def tag_words(s) :
    build = set([])
    for t in s.split(' ') :
        t = strip_out(t)
        flatten(build,t,'._')
    return [tag.lower() for tag in build if not (tag.lower() in stop_words)]

def tag_with_folder_name(obj, creator, folder_name, tag_type='') :
    tag_with(obj, creator, tag_words(folder_name), tag_type)

def tag_with(obj, creator, tags, tag_type='') :
    for tw in tags :
        tag_add(obj, tag_type, tw, creator)


# Resources 

from apps.plus_resources.models import get_or_create
from apps.plus_lib.utils import make_name

def psn_group_name(title) :
    # a special group_name maker algorithm for psn
    # compresses MHPSS 
    mhps = 'Mental Health and Psychosocial'
    if mhps in title :
        title = re.sub(mhps,'mhpss',title)

    mhps = "Mental health and psychosocial"
    if mhps in title :
        title = re.sub(mhps,'mhpss',title)
    
    r = re.compile('(.*?) Hosts$')
    m = r.match(title)
    if m :
        host_flag = True
        title = m.group(1) 

    else :
        host_flag = False
    
    s = make_name(title)
    if len(s) > 33 :
        s = s[:33]

    if host_flag :
        s = s + "_hosts"

    return s


def entity(uid) :
    return reverse[uid][1]

def e_type(uid) :
    return reverse[uid][0]

def title(uid) :
    if entity(uid).has_key('title') :
        return entity(uid)['title']
    elif e_type(uid) == 'Group' or e_type(uid) == 'Hub' :
        return entity(uid)['groupname']
    elif e_type(uid) == 'User' :
        return entity(uid)['fullname']
    else :
        return "<<entity of type %s has no title>>" % e_type(uid)

def get_creator(dict) :
    return get_user_for(dict['creatoruid'])

def swap_extension(old_file_name, new_ext) :
    parts = old_file_name.split('.')
    parts[-1] = new_ext
    return '.'.join(parts)


from django.db import transaction

@transaction.commit_on_success
def create_resource(top_container, creator, title_and_type, f_name, folder, tags=[]) :

    title = title_and_type.split('/')[-1]
    title = title.split('.',1)[0]
    name = make_name(title)
    print "Title %s, name %s, created by %s" % (title,name,creator.username)
    desc = ''
    license = 'not specified'
    author = ''
    
    try :
        f = File(open('mhpss_export/files/%s'%f_name,'rb'))
    except Exception, e:
        # in at least one case we seem to have a zip file instead of the file refered in the data
        f_name = swap_extension(f_name,'zip')
        f = File(open('mhpss_export/files/%s'%f_name,'rb'))

    resource = get_or_create(creator, top_container,
                                 resource=f, title=title, name=name, description=desc,
                                 license=license, author=author, stub=False)
       
    resource.save()
    
    f.close()
    tag_with(resource, creator, tags, '')
    return True

from reversion import revision

@transaction.commit_on_success 
@revision.create_on_success
def create_page(container, user, tags, **kwargs) :
    page = container.create_WikiPage(user,**kwargs)
    revision.comment='Import'
    revision.user = user

    tag_with(page, user, tags, tag_type='')

    return page
   
        

def load_all() :
    load_file('Folder','mhpss_export/folders.pickle')
    load_file('User','mhpss_export/users.pickle')
    load_file('Group','mhpss_export/groups.pickle')
    load_file('Hub','mhpss_export/hubs.pickle')
    load_file('File','mhpss_export/files.pickle')
    load_file('Document','mhpss_export/documents.pickle')

def get_resources_group() :
    return TgGroup.objects.get(group_name='resources')


## File names

def extract_psn_id(name) :
    name = name.split('/')[-1]
    name = name.split('.')[0]
    return name.strip('_')

from apps.plus_resources.models import Resource

def get_matching_id(file) :
    for res in Resource.objects.all() :
        res_id = extract_psn_id(res.resource.name)
        if res_id == file['uid'] :
                return res

    return None
