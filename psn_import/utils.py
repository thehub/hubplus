
import pickle

maps = {}
reverse = {}

def load_file(type,f_name) :
    xs = pickle.load(open(f_name))
    maps[type] = xs
    for x in xs :
        reverse[x['uid']] = (type,x)


def list_type(type,fields) :
    if 'all' in fields :
        print maps[type][0].keys()
    for x in maps[type] :
        for f in fields :
            if f != 'all' :
                print x[f],
        print

        
