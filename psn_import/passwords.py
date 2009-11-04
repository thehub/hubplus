from psn_import.utils import load_all, maps, reverse, get_user_for

load_all()

def get_user_from_psn_import(username):
    userdict = [u for u in maps['User'] if u['username']==username][0]
    return userdict



def patch_broken_user():
    from psn_import.users import import_user
    u1 = get_user_from_psn_import('vanommerenm')
    u2 = get_user_from_psn_import('mark.vanommeren')
    u2['email'] = '1' + u2['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('joergbaach')
    u2 = get_user_from_psn_import('jhb')
    u3 = get_user_from_psn_import('user2')
    u2['email'] = '1' + u2['email']
    u3['email'] = '2' + u3['email']
    import_user(u1)
    import_user(u2)
    import_user(u3)


    u2 = get_user_from_psn_import('sprosser')
    u3 = get_user_from_psn_import('susanprosser')
    u1 = get_user_from_psn_import('Susan')
    u2['email'] = '1' + u2['email']
    u3['email'] = '2' + u3['email'] 
    import_user(u1)
    import_user(u2)
    import_user(u3)

    u1 = get_user_from_psn_import('wrmeje')
    u2 = get_user_from_psn_import('swori')
    u2['email'] = '1' + u2['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('APSC')
    u2 = get_user_from_psn_import('sthapa')
    u2['email'] = '1' + u2['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('abdulmanaf')
    u2 = get_user_from_psn_import('manafabdul')
    u2['email'] = '1' + u2['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('synnove')
    u2 = get_user_from_psn_import('s.fredericks')
    u1['email'] = '1' + u1['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('kurt')
    u2 = get_user_from_psn_import('Kurt')
    u2['email'] = '1' + u2['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('emapalala')
    u2 = get_user_from_psn_import('emapala')
    u2['email'] = '1' + u2['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('vivi')
    u2 = get_user_from_psn_import('vivistavrou')
    u1['email'] = '1' + u1['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('lmiller')
    u2 = get_user_from_psn_import('lauramiller')
    u2['email'] = '1' + u2['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('salfield')
    u2 = get_user_from_psn_import('tsalfield')
    u2['email'] = '1' + u2['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('smudenda')
    u2 = get_user_from_psn_import('sebchikuta')
    u2['email'] = '1' + u2['email']
    import_user(u1)
    import_user(u2)

    u1 = get_user_from_psn_import('azad')
    u2 = get_user_from_psn_import('Azad')
    u1['email'] = '1' + u1['email']
    import_user(u1)
    import_user(u2)    

    u1 = get_user_from_psn_import('siphelile')
    u2 = get_user_from_psn_import('Skaseke')
    u1['email'] = '1' + u1['email']
    import_user(u1)
    import_user(u2)    

def set_password(u):
    print u['uid'], u['username'], u['email'], u['password']
    user_obj = get_user_for(u['uid'])
    user_obj.password = u['password']
    user_obj.psn_password_hmac_key = u['fullname']
    user_obj.save()

if __name__=='__main__':
    
    patch_broken_user()
    
    import ipdb

    for u in maps['User']:
        try :
            set_password(u)
        except Exception, e:
            print u
            ipdb.set_trace()


