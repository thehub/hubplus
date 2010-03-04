from django.core.exceptions import PermissionDenied

class PlusPermissionsNoAccessException(PermissionDenied):
    def __init__(self,cls,id,msg) :
        self.cls=cls
        self.id=id
        self.msg=msg
        self.silent_variable_failure = True
        self.message = msg

    def __repr__(self) :
        return "[** PlusPermissionNoAccessException: %s, %s, %s, %s **]" % (self.cls,self.id,self.msg,self.silent_variable_failure)



class PlusPermissionsReadOnlyException(PermissionDenied) : 
    def __init__(self,cls,msg) :
        self.cls = cls
        self.msg = msg

class NonExistentPermission(Exception) : 
    pass

class PlusPermissionAnonUserException(Exception):
    pass
