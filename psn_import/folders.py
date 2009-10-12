from psn_import.utils import load_file, list_type, maps, reverse

from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User

from apps.plus_resources.models import Resource, get_or_create

from apps.plus_lib.utils import make_name

from apps.plus_tags.models import tag_add

load_file('folders','mhpss_export/folders.pickle')
load_file('users','mhpss_export/users.pickle')
load_file('groups','mhpss_export/groups.pickle')

def get_for(cls, uid) :
    xs = cls.objects.filter(psn_id=uid)
    if xs.count() > 0 :
        return xs[0]
    raise Exception('not found')

def get_group_for(uid) :
    return get_for(TgGroup,uid)
    
def get_user_for(uid) :
    return get_for(User,uid)

stop_words = ['of','the','and','in','-']

def get_ultimate_container(uid) :

    try : 
        g = get_group_for(uid) 
        return g
    except Exception, e:
        try :
            u = get_user_for(uid)
            return u
        except :
            
            dict = reverse[uid]
            try :
                i = dict['parentuid']
                return get_ultimate_contained(i)
            except :
                try :
                    i = dict['mainparentuid']
                    return get_ultimate_contained(i)
                except :
                    import ipdb
                    
                    raise Exception('huh?')

def get_creator(dict) :
    return get_user_for(dict['creatoruid'])


good = 0
bad = 0

for group in maps['groups'] :
    print group['groupname'],group['uid']

for folder in maps['folders'] :
    parent_uid = folder['mainparentuid']
    print 
    print folder['title'], parent_uid
    
    print folder.keys()
    print folder['mainparenttype']
    if reverse.has_key(parent_uid) :
        parent_type = reverse[parent_uid][0]
        if parent_type == 'groups' :
            parent_group = reverse[parent_uid][1]
            print parent_type, parent_group['groupname']
            print "_)))",folder['children']
            for key,val in folder['children'].iteritems() :
                print key, val
                if '.' in val :
                    f_name = '%s.%s' % (key, val.split('.',1)[1])
                    print "Filename %s"%f_name
                    try :
                        container = get_ultimate_container(folder['parentuid'])
                        print "Fount container %s" % container
                        good = good + 1
                        creator = get_creator(folder)
                        print "Created by %s" % creator
                        title = val.split('.',1)[0]
                        name = make_name(title)
                        print "Title %s, name %s" % (title,name)
                        desc = ''
                        license = 'copyright 2009, psychosocial network'
                        author = '' 

                        f = File(open('mhpss_export/files/%s'%f_name,'rb'))
                    
                        resource = get_or_create(creator, container,  
                                                 resource=f, title=val, name=name, description=desc, 
                                                 license=license, author=author, stub=False)
                        resource.save()


                        tag_words = [s.lower() for s in folder['title'].split(' ') if (s.lower() not in stop_words)]
                        
                        for tw in tag_words:
                            tag_add(resource, 'folder', tw, creator)
                        

                    except :
                        print "******"
                        bad = bad + 1
        else :
            print "parent is not group but %s" % parent_type
    else :
        continue
        print "*** parent key not recognised"
        print folder['mainparenttype']
        print folder['mainparentuid'],folder['parentuid']
        parent_uid = folder['parentuid']
        print reverse[parent_uid]
        print "+++"


print "%s good %s bad" % (good, bad)
