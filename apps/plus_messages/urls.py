from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from messages.views import *

urlpatterns = patterns('', 
    url(r'^compose/(?P<recipient>[\+\.\w]+)/$', compose, name='messages_compose_to'),
    url(r'^all/$', in_out_trash_comp, name='messages_all'),

)
