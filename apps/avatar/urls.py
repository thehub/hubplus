from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('avatar.views',
    url('^change/$', 'change', name='avatar_change'),
    url('^(?P<group_id>[0-9]+)/change/$', 'change', name='group_avatar_change'),
    url('^delete/$', 'delete', name='avatar_delete'),
    url('^(?P<username>[\w\.\_]+)/avatar_url/$','get_url',name='avatar_url'),
)
