from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('avatar.views',
    url('^(?P<username>[\w\.\-\_]+)/change/$', 'change_user_avatar', name='avatar_change'),
    url('^(?P<group_id>[0-9]+)/change_group_avatar/$', 'change_group_avatar', name='group_avatar_change'),
    url('^delete/$', 'delete', name='avatar_delete'),
    url('^(?P<username>[\w\.\_]+)/avatar_url/$','get_url',name='avatar_url'),
)
