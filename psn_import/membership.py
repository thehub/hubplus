
from psn_import.utils import maps, reverse, load_file, load_all, title, get_group_for, get_user_for
import ipdb

load_all()

roles = set([])
if __name__ == '__main__' :
    groups = maps['Group']
    print groups[0].keys()
    for group in groups : 
        try :
            tg_group = get_group_for(group['uid'])
        except Exception, e :
            print e, group['uid']
            print group
            import ipdb
            ipdb.set_trace()
            continue
        admin = tg_group.get_admin_group()

        print group['groupname'], tg_group 
        print "owner: ",tg_group.get_ref().creator
        print admin
        
        print 'contributors',group['contributors']
        print 'members',group['members']

        print 'roles'
        print group['roles']

        for mk,mv in group['members'].iteritems() :
            print mk, mv,
            is_host = False
            try :
                user = get_user_for(mk)
                print user
                tg_group.add_member(user)

                for rk, rv in group['roles'] :
                    if 'Editor' in rv :
                        # it looks as though in cases where there are editor roles,
                        # they're given to the whole group, but let's start with the individual
                        print rk, rv
                        ipdb.set_trace()
                        if mk == rk  :
                            is_host = True
                        if rk == 'Group general':
                            is_host = True
                        if rk == 'Group stewarding-group-1.0' :
                            is_host = True
                        if is_host :
                            print "found editor"
                            print group['roles']
                            print user
                            admin.add_member(user)
                        
                        
                            


                #['TeamMember', u'Contributor', u'Editor', u'Reader', 'Owner', 'Reviewer']                                       
      

            except Exception, e:
                print e
                import ipdb
                ipdb.set_trace()
                print 

            
print roles
