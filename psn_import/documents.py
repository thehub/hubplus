import ipdb

from apps.plus_groups.models import TgGroup
from apps.plus_wiki.models import WikiPage
from psn_import.utils import load_all,maps, reverse, get_top_container, get_user_for, e_type, get_resources_group,tag_with
from apps.plus_permissions.default_agents import get_admin_user
from apps.plus_groups.models import name_from_title
from reversion import revision

@revision.create_on_success
def create_page(user,**kwargs) :
    page = container.create_WikiPage(user,**kwargs)
    revision.comment='Import'
    revision.user = user
    return page

load_all()

docs = maps['Document']
print docs[0].keys()

ipdb.set_trace()
for d in docs :
    path, tags = [],[]
    try :
        container = get_top_container(d['uid'],path,tags)
 
        print
        
        print d['title'].encode('utf-8'), container.get_display_name()
        creator_id = d['creatoruid']
        print creator_id,e_type(creator_id)
        try :
            user = get_user_for(creator_id)
        except Exception, e:
            print e
            user = get_admin_user()

        print d['creators'],creator_id,e_type(creator_id),user
        print d['body']
        keywords = d['keywords']
        if keywords  :
            print "found keywords"
            ipdb.set_trace()
            for k in keywords :
                tags.append(k)
        print 'keywords',d['keywords']
        print 'related',d['related'],':' 
        for k,v in d['related'].iteritems() :
            rel = reverse[k]
            print rel[0],rel[1]['groupname']
            
        state = d['state']
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


        page = create_page(user,title=d['title'],stub=False,license='not specified',
                           content=d['body'],in_agent=container.get_ref(),
                           name=name_from_title(d['title']),created_by=user)


        print page
        print tags
        ipdb.set_trace()
        tag_with(page, user, tags, tag_type='') 

        if flag :
            container.remove_member(user)

        print "made %s (%s) belonging to %s" % (page.title, page.id, page.in_agent.obj)

    except Exception, e :
        print e
        ipdb.set_trace()
 
