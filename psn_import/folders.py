from psn_import.utils import load_file, list_type, maps, reverse, tag_with_folder_name, create_resource, get_creator, get_top_container, load_all

from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.plus_groups.models import TgGroup
from django.contrib.auth.models import User

from apps.plus_resources.models import Resource, get_or_create

from apps.plus_lib.utils import make_name

load_all()

good = []
bad = []

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
            top = get_top_container(folder['parentuid'])
            creator = get_creator(folder)

            for key,val in folder['children'].iteritems() :
                print key, val
                if '.' in val :
                    f_name = '%s.%s' % (key, val.split('.',1)[1])
                    print "Filename %s"%f_name
                    if create_resource(top, creator, val, f_name, folder) :
                        good.append((top,creator,f_name))
                    else :
                        bad.append((top,creator,f_name))
                else :
                    import ipdb
                    ipdb.set_trace()

        else :
            print "parent is not group but %s" % parent_type
            import ipdb
            ipdb.set_trace()
    else :
        continue
        print "*** parent key not recognised"
        print folder['mainparenttype']
        print folder['mainparentuid'],folder['parentuid']
        parent_uid = folder['parentuid']
        print reverse[parent_uid]
        print "+++"


print "%s good %s bad" % (len(good), len(bad))

print "the bad"
print bad
