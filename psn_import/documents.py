import pickle
from apps.plus_groups.models import TgGroup
from apps.plus_wiki.models import WikiPage

def get_all() :
    users = pickle.load(open('mhpss_export/users.pickle'))
    groups = pickle.load(open('mhpss_export/groups.pickle'))

    return {'users':users, 'groups':groups}

def import_documents(f_name) :
    WikiPage.objects.all().delete()
    
    
    docs = pickle.load(open(f_name))
    for d in docs :
        print d.keys()
        print d['title'],d['parentpath'],d['id']
        print d['body']
    
if __name__ == '__main__' :
    import_documents('mhpss_export/documents.pickle')
    
