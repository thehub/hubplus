from psn_import.utils import load_all, maps, reverse, title, e_type, get_top_container, get_user_for, create_resource
from django.contrib.auth.models import User
from apps.plus_groups.models import TgGroup

load_all()

def list_all(all) :
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
                print folder
                import ipdb
                ipdb.set_trace()
                container = TgGroup.objects.get(group_name='resources')
                creator = main
                f_name = '%s.%s'%(folder['uid'],folder['id'].split('.')[1])
                create_resource(container, creator, folder['id'], f_name, folder, tags)
                


        if reverse.has_key(folder['parentuid']) :
            par = folder['parentuid']
            print ("parent: (%s,%s)" % (e_type(par),title(par))).encode('utf-8')
            
    

#print "Folders"
#list_all(maps['Folder'])

print "_________________________________________________"
print "Files"
try :
    list_all(maps['File'])
except Exception, e:
    print e
    import ipdb
    ipdb.set_trace()

print len(maps['File'])
