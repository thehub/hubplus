from psn_import.utils import load_all, reverse, maps, get_group_for, get_top_container, title as e_title
from psn_import.files import make_file_name

from apps.plus_resources.models import Resource
from apps.plus_wiki.models import WikiPage

import ipdb

load_all()

def extract_psn_id(name) :
    name = name.split('/')[-1]
    name = name.split('.')[0]
    return name.strip('_')

def get_matching_id(file) :
    for res in Resource.objects.all() :
        res_id = extract_psn_id(res.resource.name)
        if res_id == file['uid'] : 
            return res
        
    return None


def check_files(lst) :
    missing = []
    count = 0
    for file in lst :
        match = get_matching_id(file)
        if not match :
            missing.append({'uid':file['uid'],'title':file['title'],'mainparentuid':file['mainparentuid']})
            print get_top_container(file['uid'],[],[])
            print e_title(file['mainparentuid'])
        else :
            count = count + 1
    for m in missing :
        print m
    print "There are %s uploads missing" % len(missing)
    print "%s are ok" % count


def match_page_and_document(document) :
    title = document['title']
    for p in WikiPage.objects.all() :
        if title[0:4] == p.name[0:4] :
            print title,p.name, p.title

def check_documents(lst) :
    for doc in lst :
        print doc['title'],
        match = match_page_and_document(doc)
        break

if __name__ == '__main__' :
    try :
        check_files(maps['File'])
        #check_documents(maps['Document'])
    except Exception, e:
        print e



