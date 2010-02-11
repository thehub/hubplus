from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'apps.synced.login', name="acct_login"),
    url(r'^on_create_user/$', 'remote_syncing.views.on_create_user', name='on_create_user'),
    url(r'^on_user_changed/$', 'remote_syncing.views.on_user_changed', name='on_user_changed'),

    url(r'^on_create_group/$', 'remote_syncing.views.on_create_group', name='on_create_group'),
    url(r'^on_group_changed/$', 'remote_syncing.views.on_group_changed', name='on_group_changed'),

    url(r'^on_join_group/$', 'remote_syncing.views.on_join_group', name='on_join_group'),
    url(r'^on_leave_group/$', 'remote_syncing.views.on_leave_group', name='on_leave_group'),


)
