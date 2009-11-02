from psn_import.utils import load_all, maps, reverse

load_all()

for u in maps['User'] :                                                                                                     
    username = u['username']                                                                                                
    pw = u['password']                                                                                                      
    full = u['fullname']
    print username, pw, full, u['uid']
