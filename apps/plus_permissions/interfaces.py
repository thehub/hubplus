"""
Interfaces are like roles. They group together various Read/Write/Call options for assignment. We should access content objects through an interface, which acts as a mask on the object.

Interfaces are associated with a SecurityContext via a SecurityTag. Agents (users and groups) get access to them by being associated with a security tag via the (Agent object). Agents can acquire interfaces by being a "member of" another agent with access to them.  

Interfaces are namespaced by the type they apply to e.g. "Wiki.Editor" allowing us to assign permissions on a type.  The syntax ".Editor" refers to the Editor Interface on the SecurityContext target object. The syntax *.Editor refers to the Editor interface on any objects in the security context.
"""

__all__ = ['secure_wrap', 'PlusPermissionsNoAccessException', 'PlusPermissionsReadOnlyException', 'add_type_to_interface_map', 'add_interfaces_to_type', 'strip']

type_interfaces_map = {}  

def get_interface_map(cls):
    return interface_map.get(cls.__name__, {})

def add_type_to_interface_map(cls, interfaces):
    type_interfaces_map[cls.__name__] = {}
    add_interfaces_to_type(cls, interfaces)
        
def add_interfaces_to_type(cls, interfaces):
    if not isinstance(list, interfaces):
        raise TypeError
    type_interfaces = type_interfaces_map[cls.__name__]
    for interface in interfaces:
        if interface[0] not in type_interfaces:
            type_interfaces[interface[0], interface[1]]
        else:
            raise "Interface "+ interface  +"was not added to "+ class +" because an interface of that name already exists"

def secure_wrap(content_obj, interface_names=None):
    access_obj = NullInterface(content_obj)
    access_obj.load_interfaces_for(request.user, interface_names=interface_names)
    return access_obj

def strip(x) :
    """If x is really a Null interface, return the inner value, otherwise, return itself"""
    try : 
        return x.get_inner()
    except :
        return x


class PlusPermissionsNoAccessException(Exception):
    def __init__(self,cls,id,msg) :
        self.cls=cls
        self.id=id
        self.msg=msg
        self.silent_variable_failure = True

class PlusPermissionsReadOnlyException(Exception) : 
    def __init__(self,cls,msg) :
        self.cls = cls
        self.msg = msg


class InterfaceReadProperty:
    """ Add this to a NullInterface to allow a property to be readable"""
    pass

class InterfaceWriteProperty:
    """ Add this to a NullInterface to allow a property to be writable """
    pass

class InterfaceCallProperty:
    """ Add this to a NullInterface to allow a property to be called """
    pass


class Interface :

    @classmethod
    def delete(self) :
        return False

    @classmethod
    def has_property_name_and_class(self, name, cls) :
        """Does this object have a property of name 'name' and class 'cls'?"""
        for k,v in self.__dict__.iteritems() :
            if k == name and v.__class__ == cls :
                return True
        return False

    @classmethod
    def has_write(self,name) :
        return self.has_property_name_and_class(name,InterfaceWriteProperty)

    @classmethod
    def has_read(self,name) :
        return self.has_property_name_and_class(name,InterfaceReadProperty)

    @classmethod
    def has_call(self,name) :
        return self.has_property_name_and_class(name,InterfaceCallProperty)
        
    @classmethod
    def get_id(cls) : 
        raise UseSubclassException(Interface,'You need a subclass of Interface that implements its get_id')
        


class NullInterface :
    """
    Empty interface, wraps models in a shell, which only lets explicitly named properties through
    """
    def __init__(self, inner) :
        self._inner = inner
        self._interfaces = []        
        self._exceptions = [ 
            lambda x : x[0] == '_',
            lambda x : x == 'id',
            lambda x : x == 'save',
        ]

    def get_inner(self) :
        return self._inner

    def get_inner_class(self) :
        return self.get_inner().__class__

    def get_interfaces(self) :
        return self._interfaces

    def load_interfaces_for(self, agent, interface_names=None) :
        """Load interfaces for the wrapped inner content that are available to the agent"""
        resource = self.get_inner()
        cls = resource.__class__
        interface_map = type_interfaces_map[cls]
        if not interface_names:
            interface_names = interface_map.keys()
        for name in interface_names:
            interface = interface_map[name]
            if ps.has_access(agent=agent, resource=resource, interface=ps.get_interface_id(self.get_inner().__class__,k)) :
                self.add_interface(v)
    
    def construct_permissions(self):
        for interface in self.

    
    def __getattr__(self,name) :
        for rule in self.__dict__['_exceptions'] :
            if rule(name) :
                return self.get_inner().__getattribute__(name)
        if self.fold_interfaces(lambda a, i : a or i.has_read(name) or i.has_call(name), False) :
            return self.get_inner().__getattribute__(name)
        raise PlusPermissionsNoAccessException(self.get_inner_class(),name,'from __getattr__')

    def __setattr__(self,name,val) :
        if self.fold_interfaces(lambda a,i : a or i.has_write(name),False) :
            self.get_inner().__setattr__(name,val)
            return None      
        raise PlusPermissionsReadOnlyException(self.get_inner_class(),name)        

    def add_interface(self, interface) :
        """NOT USED atm, adds a new interface to the object whilst it is wrapped
        """
        self._interfaces.append(interface)
        self.load_interfaces(interface)

    def remove_interface(self, cls):
        """NOT USED atm, emove an interface from the object whilst it is wrapped
        """
        self._interfaces.remove(interface)
        self.load_interfaces(interface)
        


