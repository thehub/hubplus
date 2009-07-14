from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<group_id>[\w\._-]+)/$', 'plus_groups.views.group', name='group'),
)

