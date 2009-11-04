from copy import deepcopy

def overlay(d, d2) :
    """ Recursively overlay one dictionary with another           
    Rules : if d2 has things not in d, add them     
            if d and d2 have value which *isn't* a dictionary, d2 over-rides d
            if d and d2 have item which is a dictionary, 
                        recursively overlay value from d with d2"""
    nd = deepcopy(d)
    for k,v in d2.iteritems() :
        if not nd.has_key(k) :
            nd[k] = v
        elif nd[k].__class__ == dict and d2.__class__ == dict :
            nd[k] = overlay(nd[k],d2[k])
        else :
            nd[k] = d2[k]
    return nd

