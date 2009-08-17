
from django.conf.urls.defaults import *

urlpatterns = patterns("",
    #url(r"^failure/$", )
    url(r"^invite/$","signup_codes.views.admin_invite_user",name='signup_invite_form')
                    
)
