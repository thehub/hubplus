
from apps.plus_permissions.default_agents import get_anon_user 

class AnonUserMiddleware(object) :
    def process_request(self, request):

        if not request.user.is_authenticated() :
            request.user = get_anon_user()
        return None
