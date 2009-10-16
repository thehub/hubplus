from psn_import.utils import load_file, list_type, maps, reverse, get_for, get_group_for

from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User

from apps.plus_resources.models import Resource, get_or_create

from apps.plus_lib.utils import make_name, tag_with_folder_name

from apps.plus_tags.models import tag_add

from apps.plus_resources.models import Resource

load_file('folders','mhpss_export/folders.pickle')
load_file('users','mhpss_export/users.pickle')
load_file('groups','mhpss_export/groups.pickle')
load_file('hubs','mhpss_export/hubs.pickle')
load_file('files','mhpss_export/files.pickle')


def show(f) :
    print "*",f['mainparenttype'],f['mainparentuid'],f['id'],f['mainparentpath'],f['parenttype'],f['parentuid']

def test_resource(title) :
    rs = Resource.objects.filter(title=title)
    if len(rs) > 1 :
        raise Exception('two resources with same title : %s'%title)
    if rs :
        print "exists %s (%s)" % (rs[0].title, rs[0].id)
        return True
    else :
        print "no resource called %s" % title
        return False

for f in maps['files'] :
    #print f.keys()

    flag = True
    
    title = f['title']
    print
    if not test_resource(title) :
        show(f)
        import ipdb
        ipdb.set_trace()
        if f['mainparenttype'] == 'Group' :
            print  "main group %s" % get_group_for(f['mainparentuid'])
            flag = False
        
        if f['parenttype'] == 'Group' :
            print "parent group %s" % get_group_for(f['parentuid'])
            flag = False
        else :
            print 'parent is ',f['parenttype']
            parent = reverse[f['parentuid']][1]
            
            if f['parenttype']== 'Group' :
                title  = parent['title']

            elif f['parenttype']=='Folder' :
                title = parent['title']

            elif f['parenttype']=='HubUser' :
                title = parent['username']
            else :
                title = "<<<name>>> from %s" % parent.keys()

            print title
            

        

        if flag:
            print "***"
