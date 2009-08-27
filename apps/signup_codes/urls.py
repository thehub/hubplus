
from django.conf.urls.defaults import *

urlpatterns = patterns("",
    #url(r"^failure/$", )
    url(r"^invite/$","signup_codes.views.admin_invite_user",name='signup_invite_form'),
    url(r'^(?P<resource_id>[0-9]+)/$', 'apps.signup_codes.views.proxied_signup', name='proxied_signup'),
                    
)
