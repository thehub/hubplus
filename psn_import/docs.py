import sys

from psn_import.utils import maps, reverse, load_file, list_type, get_user_for, get_group_for

def get_ultimate_container(uid) :
    print "%s is a %s" % (uid, reverse[uid][0])
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
                    print "Can't find ultimate parent for"
                    raise(Exception('huh? %s' % (uid)))
                    
                
                
import ipdb
if __name__ == '__main__' :
    load_file('users','mhpss_export/users.pickle')
    load_file('groups','mhpss_export/groups.pickle')
    load_file('hubs','mhpss_export/hubs.pickle')
    load_file('folders','mhpss_export/folders.pickle')
    load_file('documents','mhpss_export/documents.pickle')
    load_file('files','mhpss_export/files.pickle')
    n_folders = 0
    n_children = 0
    
    for r,v in reverse.iteritems() :
        print r, v[0]
    
    for d in maps['folders'] :
       
        n_folders = n_folders+1
        if d.has_key('children') :
            try :
                print d['title'],get_ultimate_container(d['uid']) 
                for k,v in d['children'].iteritems() :
                    n_children = n_children+1
                    print k,v
            except Exception, e:
                pass
                #print e
    print "there are %s children in %s folders" % (n_children, n_folders) 



