import ipdb

from apps.plus_groups.models import TgGroup
from apps.plus_wiki.models import WikiPage
from psn_import.utils import load_all,maps, reverse, get_top_container, get_user_for, e_type, get_resources_group,tag_with, create_page
from apps.plus_permissions.default_agents import get_admin_user
from apps.plus_groups.models import name_from_title



load_all()

docs = maps['Document']
print docs[0].keys()

log= []
related_dict = {}
for doc in docs :
    path, tags = [],[]
    try :
        container = get_top_container(doc['uid'],path,tags)
        print
        print doc['title'].encode('utf-8'), container.get_display_name()
        creator_id = doc['creatoruid']
        if creator_id == -1 or creator_id == '-1' :
            user = get_admin_user()
        else :
            print creator_id,e_type(creator_id)

            try :
                user = get_user_for(creator_id)
            except Exception, e:
                print e
                user = get_admin_user()

        print doc['creators'],creator_id,user
        print doc['body']
        keywords = doc['keywords']
        if keywords  :
            print "found keywords"
            ipdb.set_trace()
            for k in keywords :
                tags.append(k)
        print 'keywords',doc['keywords']
        print 'related',doc['related'],':' 
        for k,v in doc['related'].iteritems() :
            rel = reverse[k]
            print rel[0],rel[1]['groupname']
            
        state = doc['state']
        print "state",state

        flag = False

        if container.__class__.__name__ == 'User' :
            tags.append(container.username)
            tags.append(container.first_name)
            tags.append(container.last_name)
            user = container
            container = get_resources_group()

        if not container.has_member(user) :
            container.add_member(user)
            flag = True

        title = doc['title']
        if len(title) > 80 :
            title = title[:80]
            print "shortened %s" % title
        name = name_from_title(title)

        pages = WikiPage.objects.filter(name=name)
        if not pages :
            page = create_page(container, user, tags, 
                           title=title, stub=False, license='not specified',
                           content=doc['body'], in_agent=container.get_ref(),
                           name=name, created_by=user)
        else : 
            page = pages[0]
            
        related_dict[page.id] = (doc['uid'],doc['related'])
        if flag :
            container.remove_member(user)

        print "made %s (%s) belonging to %s" % (page.title, page.id, page.in_agent.obj)

    except Exception, e :
        print e
        log.append(doc['uid'])
        ipdb.set_trace()
 

print "Finished"
print log
for k,v in related_dict.itervalues() :
    print k,v
