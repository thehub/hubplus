
from psn_import.utils import maps, reverse, load_all, get_top_container, psn_group_name, e_type
from psn_import.utils import title as e_title

from apps.plus_resources.models import Resource
import ipdb

userlog = []
if __name__ == '__main__' :
    load_all()
    for upload in maps['File'] :
        print 
        uid = upload['uid']
        title = upload['title']
        related = upload['related']        
            
        container = get_top_container(uid,[],[])
        
        print container, title.encode('utf-8'), related
        
        mainparentuid =  upload['mainparentuid']
        if reverse.has_key(mainparentuid) :
            print "mainparent %s, %s" % (e_type(mainparentuid),e_title(mainparentuid))
            mainparent = reverse[mainparentuid]
            try :
                if mainparent[1]['groupname'] != 'RESOURCES' :
                    print "Main parent title %s" % mainparent[1]['groupname']
            except Exception, e :
                print e
                if e_type(mainparentuid) == 'User' :
                    userlog.append({'uid':uid,'mainparentuid':mainparentuid,'owner':e_title(mainparentuid)})
                else :
                    print e
                    ipdb.set_trace()
                
        else :
            print "no reverse for %s" % uid
            ipdb.set_trace()
        
        title_without_type = '.'.join(title.split('.')[:-1])
        #title_without_type = title_without_type.replace('-','_')
        #title_without_type = title_without_type.replace(' ','_')
        print title_without_type.encode('utf-8')
        res = Resource.objects.filter(title__startswith=title_without_type)
        if res :
            if len(res)==1 :
                r = res[0]
                if r.in_agent.obj.id != container.id or r.in_agent.obj.__class__ != container.__class__ :
                    print "a resource with matching title, but different container"
                    print r, r.title, r.in_agent.obj
                    ipdb.set_trace()
            else :
                print "too many matching resources"
                print res
                #ipdb.set_trace()
        else :
            print "no matching resource"
            print title.encode('utf-8')
            ipdb.set_trace()
            
print userlog
