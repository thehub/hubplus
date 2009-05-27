from django.db import models


class Interface :
    def __init__(self,name):
        self.name = name


class BlogPost :
    interfaces = {
        'viewer':Interface('viewer'),
        'editor':Interface('editor'),
        'commentor':Interface('commentor')
        }

    def __init__(self,name) :
        self.name = name



class SecurityTag(models.Model) :


    def __init__(self,name) :
        self.name = name
        self.resources = []
        self.records = []

    def addResources(self,rs) :
        for r in rs: 
            if r not in self.resources : 
                self.resources.append(r)

    def appliesTo(self,res) :
        return res in self.resources

    def IoN(self,i,res) :
        # if variable i is not an Interface object, we guess it evaluates to 
        # the name of an interface in the dictionary of the resource
        if i.__class__ != Interface : return res.interfaces[i]
        return i

    def giveAccess(self,agent,resource,interface) :
        interface = self.IoN(interface,resource)
        if not self.hasAccess(agent,resource,interface) :
            self.records.append((agent,resource,interface))
            self.addResources([resource])
                
    def hasAccess(self,agent,resource,interface) :
        interface = self.IoN(interface,resource)
        for a,r,i in self.records : 
            if i != interface : continue
            if r != resource : continue
            if a == agent : return True
            if agent.isMemberOf(a) : return True
        return False

    def __str__(self) :
        return """Resources : %s
Records : %s
""" % (self.resources,self.records)

