
from apps.plus_groups.models import TgGroup
from apps.plus_wiki.models import WikiPage
from psn_import.utils import load_all,maps, reverse, get_top_container, get_user_for, e_type
from apps.plus_permissions.default_agents import get_admin_user


load_all()


docs = maps['Document']
print docs[0].keys()

import ipdb
ipdb.set_trace()

for d in docs :
    path, tags = [],[]
    try :
        container = get_top_container(d['uid'],path,tags)
 
        print
        
        print d['title'].encode('utf-8'), container.get_display_name()
        try :
            user = get_user_for(d['creatorid'])
        except Exception, e:
            print e
            user = get_admin_user()

        print d['creators'],d['creatoruid'],e_type(d['creatoruid']),get_user_for(d['creatoruid'])
        print d['body']
        print d['keywords']
        print d['related'],':' 
        for k,v in d['related'].iteritems() :
            rel = reverse[k]
            print rel[0],rel[1]['groupname']
            
        print d['state']
        print tags
        flag = False
        if not container.has_member(user) :
            container.add_member(user)
            flag = True
            container.create_WikiPage(user,title=d['title'],stub=False,license='

        if flag :
            container.remove_member(user)
        
    except Exception, e :
        print e
        ipdb.set_trace()
 
