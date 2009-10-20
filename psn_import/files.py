from psn_import.utils import load_all, maps, reverse, title, e_type, get_top_container, get_user_for, create_resource
from django.contrib.auth.models import User
from apps.plus_groups.models import TgGroup
from apps.plus_permissions.default_agents import get_all_members_group

load_all()


def make_file_name(id,uid) :
    if '.' in id :
        fids = id.split('.')
        ext = fids[-1]
        #'.'.join(fids[1:])
        
        if ext == 'doc' or ext == 'DOC':
            ext = 'msword'
        if ext == 'xls' :
            ext = 'vnd.ms-excel'
        if ext == 'ppt' :
            ext = 'vnd.ms-powerpoint'
        if ext == 'PDF' :
            ext = 'pdf'
        if ext == 'htm' :
            ext = 'html'
        

    else :
        front = id
        ext = ''
        fids = [front,'']

    f_name = '%s.%s'%(uid,ext)
    print "*",f_name
    try :
        f = open('mhpss_export/files/%s'%f_name)
        f.close()
        return f_name
    except Exception, e:
        print e
        try :
            f_name = '%s.%s' % (uid,fids[-1])
            f = open('mhpss_export/files/%s'%f_name)
            f.close()
            return f_name
        except Exception, e:
            import ipdb
            ipdb.set_trace()
    
    return "nofile"

def import_all(all) :
    log= []
    for folder in all :
        print

        print ('%s, %s, %s, %s, %s' % (folder['title'], folder['mainparentuid'], folder['mainparenttype'], folder['parentuid'], folder['parenttype'])).encode('utf-8')
        if reverse.has_key(folder['mainparentuid']) :
            mainpar = folder['mainparentuid']
            print ("main parent: (%s,%s)" % (e_type(mainpar),title(mainpar))).encode('utf-8')
            if title(mainpar) != 'RESOURCES' :
                print title(mainpar).encode('utf-8')

            path  = []
            tags = []
            main = get_top_container(folder['uid'],path,tags)
            print (','.join(path)).encode('utf-8')
            print (','.join(['%s'% t for t in tags])).encode('utf-8')


            if main.__class__ == User :
                container = TgGroup.objects.get(group_name='resources')
                creator = main
                f_name=make_file_name(folder['id'],folder['uid']) 

                try :
                    create_resource(container, creator, folder['id'], f_name, folder, tags)
                except Exception, e:
                    print e
                    import ipdb
                    ipdb.set_trace()
                    log.append(folder['uid'])

            elif main.__class__ == TgGroup :
                print "((()))",tags
                container = main
                creator = get_user_for(folder['creatoruid'])
                site_hosts = get_all_members_group().get_admin_group()
                if not creator.is_member_of(site_hosts) :
                    site_hosts.add_member(creator)
                    flag = True
                else :
                    flag = False

                f_name = make_file_name(folder['id'],folder['uid'])
                try :
                    create_resource(container, creator, folder['id'], f_name, folder, tags)
                except Exception, e :
                    print e
                    import ipdb
                    ipdb.set_trace()
                    log.append(folder['uid'])

                if flag :
                    site_hosts.remove_member(creator)



        if reverse.has_key(folder['parentuid']) :
            par = folder['parentuid']
            print ("parent: (%s,%s)" % (e_type(par),title(par))).encode('utf-8')
            
    
        print "Errors"
        print log
#print "Folders"
#list_all(maps['Folder'])

print "_________________________________________________"
print "Files"
try :
    
    print reverse['d5e427e5a91bf09b160cb4d4254c094f']
    import ipdb
    ipdb.set_trace()
    import_all(maps['File'])
except Exception, e:
    print e
    import ipdb
    ipdb.set_trace()

print len(maps['File'])
