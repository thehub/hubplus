
from models import *


class PlusPermissions :
    
    def process_request(self, request) :
        ps = PermissionSystem()
        u = request.user

    def process_view(self, request, view_func, view_args, view_kwargs) :
        pass

    def process_response(self, request, response) :
        return response

    def process_exception(self, request, exception) :
        pass

