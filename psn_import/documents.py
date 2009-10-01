import pickle
from apps.plus_groups.models import TgGroup
from apps.plus_wiki.models import WikiPage


def import_documents(f_name) :
    WikiPage.objects.all().delete()
    
    docs = pickle.load(open(f_name))
    for d in docs :
        print d.keys()
        print d['title'],d['parentpath'],d['id']
        print d['body']
    
    
    
if __name__ == '__main__' :
    import_documents('mhpss_export/documents.pickle')
    
