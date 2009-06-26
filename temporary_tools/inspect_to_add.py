
f = open('inspect.txt')
flag = False
for x in f.readlines() :
   
    if flag and x.find('class') == 0 :
        flag = False

    if x.find('class TgUser(') == 0 :
        flag = True

    if flag :
        if x.find(' = ') > 0 :
            (name,type) = x.split(' = ')
            if name.strip() == 'db_table' : break
            if type.find('#') > 0 :
                type = (type.split('#'))[0]
            print "User.add_to_class('%s',%s)" % (name.strip(),type.strip())

    
