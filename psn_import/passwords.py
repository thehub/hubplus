from psn_import.utils import load_all, maps, reverse

from hashlib import sha1
import hmac as create_hmac

load_all() 

def encrypt(name, password):
    return create_hmac.new(name, password, sha1).hexdigest()
    

#for u in maps['User'] :
#    username = u['username']
#    pw = u['password']
#    full = u['fullname']#

#    print username, pw, full

syn = [u for u in maps['User'] if u['username']=='s.fredericks'][0]
print syn
pw = syn['password']
full = syn['fullname']
print pw
print encrypt(full,'artista')
