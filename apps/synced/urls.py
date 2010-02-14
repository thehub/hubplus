from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'apps.synced.login', name="acct_login"),

    url(r'^synced/on_user_create/$', 'synced.views.on_user_create', name='on_user_create'),
    url(r'^synced/on_user_change/$', 'synced.views.on_user_change', name='on_user_change'),

    url(r'^synced/on_group_join/$', 'synced.views.on_group_join', name='on_group_leave'),
    url(r'^synced/on_group_leave/$', 'synced.views.on_group_leave', name='on_group_leave'),

)
