from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from messages.views import *

urlpatterns = patterns('', 
    url(r'^compose/(?P<recipient>[\+\.\w]+)/$', compose, name='messages_compose_to'),
)
