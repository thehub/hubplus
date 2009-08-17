"""
Interfaces are like roles. They group together various Read/Write/Call options for assignment. We should access content objects through an interface, which acts as a mask on the object.

Interfaces are associated with a SecurityContext via a SecurityTag. Agents (users and groups) get access to them by being associated with a security tag via the (Agent object). Agents can acquire interfaces by being a "member of" another agent with access to them.  

Interfaces are namespaced by the type they apply to e.g. "Wiki.Editor" allowing us to assign permissions on a type.  The syntax ".Editor" refers to the Editor Interface on the SecurityContext target object. The syntax *.Editor refers to the Editor interface on any objects in the security context.
"""

__all__ = ['secure_wrap', 'PlusPermissionsNoAccessException', 'PlusPermissionsReadOnlyException', 'add_type_to_interface_map', 'add_interfaces_to_type', 'strip', 'TemplateSecureWrapper', 'get_interface_map']


def secure_wrap(content_obj, interface_names=None):
    access_obj = SecureWrapper(content_obj)
    access_obj.load_interfaces_for(request.user, interface_names=interface_names)
    return access_obj


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

class NonExistentPermission(Exception) : 
    pass


class TemplateSecureWrapper:

    def __init__(self, SecureWrapper):
        self.SecureWrapper = SecureWrapper

    def __getattr__(self, name):
        try:
            return getattr(self.SecureWrapper, name)
        except:
            return NotViewable


type_interfaces_map = {}  

def get_interface_map(cls):
    if not isinstance(cls, basestring):
        cls = cls.__name__
    return type_interfaces_map.get(cls, {})

def add_type_to_interface_map(cls, interfaces):
    print "adding %s to %s in interface map" % (','.join(interfaces),cls.__name__)
    type_interfaces_map[cls.__name__] = {}
    add_interfaces_to_type(cls, interfaces)
        
def add_interfaces_to_type(cls, interfaces):
    if not isinstance(interfaces, dict):
        raise TypeError
    type_interfaces = type_interfaces_map[cls.__name__]
    for label, interface in interfaces.iteritems():
        if label not in type_interfaces:
            type_interfaces[label] = interface
        else:
            raise "Interface "+ label  +"was not added to "+ `cls` +" because an interface of that name already exists"

    print "ZZZ",type_interfaces


def strip(x) :
    """If x is really a Null interface, return the inner value, otherwise, return itself"""
    try : 
        return x.get_inner()
    except :
        return x




class InterfaceReadProperty:
    """ Add this to a SecureWrapper to allow a property to be readable"""
    pass

class InterfaceWriteProperty:
    """ Add this to a SecureWrapper to allow a property to be writable """
    pass

class InterfaceReadWriteProperty:
    """ Add this to a SecureWrapper to allow a property to be writable """
    pass

class InterfaceCallProperty:
    """ Add this to a SecureWrapper to allow a property to be called """
    pass

        
class NotViewable:
    @classmethod
    def __str__(self):
        return ""

    @classmethod
    def __repr__(self):
        return ""

    
    

class SecureWrapper:
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
        self._permissions = {InterfaceReadProperty: set(),
                             InterfaceCallProperty: set(),
                             InterfaceWriteProperty: set(),
                             InterfaceReadWriteProperty: set()}

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
        for iname in interface_names:
            interface = interface_map[iname]
            if has_access(agent=agent.get_ref(), resource=resource, interface=self.get_inner.__class__ + '.' + iname) :
                self.add_permissions(interface)
    
    def add_permissions(self, interface):
        for attr, perm in interface.__dict__:
            try:
                permitted = self._permissions[perm]
            except KeyError:
                if attr.startswith('_'):
                    pass
                else:
                    raise NonExistentPermission
            else:
                if attr not in permitted:
                    perms.add(attr)

    def has_permission(self, name, interface) :
        """The moment of truth!"""
        try: 
            perms = self._permissions[interface]
        except KeyError:
            raise NonExistentPermission
        else:
            if name in perms:
                return True
            return False
                        
    def __getattr__(self, name):
        for rule in self.__dict__['_exceptions']:
            if rule(name) :
                return self.get_inner().__getattribute__(name)

        if self.has_permission(name, InterfaceReadProperty) or self.has_permission(name, InterfaceReadWriteProperty):
            return self.get_inner().__getattribute__(name)

        elif self.has_permission(name, InterfaceCallProperty):
            return self.get_inner().__getattribute__(name)

        raise PlusPermissionsNoAccessException(self.get_inner_class(),name,'from __getattr__')

    def __setattr__(self, name, val):
        if self.has_permission(name, InterfaceWriteProperty) or self.has_permission(name, InterfaceReadWriteProperty):
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
