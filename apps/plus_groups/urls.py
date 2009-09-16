from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^create/$', 'plus_groups.views.create_group', name='create_group'),
                       url(r'^create_object/$', 'plus_groups.views.add_content_object', name="add_content_object"),
                       url(r'^(?P<resource_id>[\d]+)/page/', include('apps.plus_wiki.urls')),
                       url(r'^(?P<resource_id>[\d]+)/add_content/$', 'plus_groups.views.add_content_form', name="add_content"),
                       url(r'^(?P<resource_id>[\w\._-]+)/add_member/(?P<username>[\w\._-]+)/$', 'plus_groups.views.add_member', 'add_member'),
                       url(r'^autocomplete/$', 'plus_groups.views.autocomplete', name="autocomplete_group"),
                       url(r'^(?P<resource_id>[\w\._-]+)/$', 'plus_groups.views.group', name='group'),
                       url(r'^(?P<resource_id>[\w\._-]+)/join/$', 'plus_groups.views.join', name='join_group'),
                       url(r'^(?P<resource_id>[\w\._-]+)/apply/$', 'plus_groups.views.apply', name='apply_group'),
                       url(r'^(?P<resource_id>[\w\._-]+)/leave/$', 'plus_groups.views.leave', name='leave_group'),
                       url(r'^(?P<resource_id>[\w\._-]+)/invite/$', 'plus_groups.views.invite', name='invite_to_group'),    
                       url(r'^$', 'plus_groups.views.groups', name='groups'),
                       )

