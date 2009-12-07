
from apps.plus_permissions.default_agents import get_anon_user 

class AnonUserMiddleware(object) :
    def process_response(self, request, response):
        if not request.user.is_authenticated() :
            request.user = get_anon_user()
        return response
