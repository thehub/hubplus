from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from messages.views import *

urlpatterns = patterns('',
    #url(r'^$', redirect_to, {'url': 'inbox/'}),
    url(r'^inbox/$', inbox, name='messages_inbox'),
    url(r'^outbox/$', outbox, name='messages_outbox'),
    url(r'^compose/$', compose, name='messages_compose'),
    url(r'^compose/(?P<recipient>[\+\w]+)/$', compose, name='messages_compose_to'),
    url(r'^reply/(?P<message_id>[\d]+)/$', in_out_trash_comp, name='messages_reply'),
    url(r'^view/(?P<message_id>[\d]+)/$', view, name='messages_detail'),
    url(r'^delete/(?P<message_id>[\d]+)/$', delete, name='messages_delete'),
    url(r'^undelete/(?P<message_id>[\d]+)/$', undelete, name='messages_undelete'),
    url(r'^trash/$', trash, name='messages_trash'),
    url(r'^$', in_out_trash_comp, name='messages_all'),
    url(r'^to/(?P<recipient>[\+\w\.\_\-]+)/$', in_out_trash_comp, name="messages_all_to"),


)
