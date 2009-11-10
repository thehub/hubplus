from psn_import.utils import load_all, reverse, maps, get_group_for, get_top_container, title as e_title
from psn_import.utils import get_matching_id

from psn_import.files import make_file_name

from apps.plus_resources.models import Resource
from apps.plus_wiki.models import WikiPage

from apps.plus_groups.models import name_from_title

import ipdb

load_all()


def check_files(lst) :
    missing = []
    misplaced = []
    accounted = 0
    well_placed=0

    for file in lst :
        match = get_matching_id(file)

        uid = file['uid']
        container = get_top_container(uid,[],[])

        if not match :

            missing.append({'uid':uid,'title':file['title'],'mainparentuid':file['mainparentuid']})
            print container, e_title(file['mainparentuid'])
            print file['title'].encode('utf-8')

        else :

            accounted=accounted+1
            real_container = match.in_agent.obj
            if real_container != container :
                print real_container, container
                misplaced.append({'upload':match,'owner':match.created_by, 'in':real_container,'ought':container})
            else :
                well_placed = well_placed + 1

    for m in missing :
        print m
    print "There are %s uploads missing" % len(missing)
    print "%s are ok" % accounted
    for m in misplaced :
        print m
    print "There are %s uploads misplaced" % len(misplaced)
    print "%s are well placed" % well_placed


def match_page_and_document(document) :
    title = document['title']
    name = doc_name_from_title(title)

    for p in WikiPage.objects.all() :
        if name == p.name :
            return p
    return None

def check_documents(lst) :
    for doc in lst :
        print doc['title'],
        match = match_page_and_document(doc)
        break

def doc_name_from_title(title) :
    if len(title) > 80 :
        title = title[:80]
    return name_from_title(title)

def check_documents(lst) :
    missing = []
    accounted = 0
    misplaced = []
    well_placed = 0
    for doc in lst :
        try:
            container = get_top_container(doc['uid'],[],[])
            title = doc['title']
            name = doc_name_from_title(title)
            match = match_page_and_document(doc)
            if not match :
                missing.append({'title':title})
            else :
                accounted = accounted + 1
                if match.in_agent.obj != container :
                    misplaced.append({'doc':match,'is':match.in_agent.obj,'ought':container})
                else :
                    well_placed = well_placed+1
        except Exception, e:
            print e
            ipdb.set_trace()
    for m in missing :
        print m
    print "%s accounted ok" % accounted
    for m in misplaced :
        print m
    print "%s well placed " % well_placed


if __name__ == '__main__' :
    try :
        check_files(maps['File'])
        check_documents(maps['Document'])

    except Exception, e:
        print e



