import pickle
from apps.plus_groups.models import TgGroup
from apps.plus_wiki.models import WikiPage


def import_documents(f_name) :
    docs = pickle.load(open(f_name))
    for d in docs :
        print d.keys()
        print d



import sys

if __name__ == '__main__' :
    print sys.argv    
    import_documents('mhpss_export/%s' % sys.argv[3])
    exit()



