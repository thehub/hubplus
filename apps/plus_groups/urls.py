from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^create/$', 'plus_groups.views.create_group', name='create_group'),
                       url(r'^create_hub/$', 'plus_groups.views.create_group', {'is_hub':True}, name='create_hub'),
                       url(r'^create_object/$', 'plus_groups.views.add_content_object', name="add_content_object"),
                       
                       url(r'^group_type_ajax/$', 'plus_groups.views.group_type_ajax', name='group_type_ajax'),


                       url(r'^(?P<resource_id>[\d]+)/page/', include('apps.plus_wiki.urls')),
                       url(r'^(?P<resource_id>[\d]+)/upload/', include('apps.plus_resources.urls')),
                       url(r'^(?P<resource_id>[\d]+)/applications/', include('apps.plus_contacts.urls')),
                       url(r'^(?P<resource_id>[\d]+)/add_content/$', 'plus_groups.views.add_content_form', name="add_content"),
                       url(r'^(?P<resource_id>[\w\._-]+)/add_member/(?P<username>[\w\._-]+)/$', 'plus_groups.views.add_member', name='add_member'),
                       url(r'^autocomplete/$', 'plus_groups.views.autocomplete', name="autocomplete_group"),
                       url(r'^(?P<resource_id>[\w\._-]+)/$', 'plus_groups.views.group', name='group'),
                       url(r'^(?P<resource_id>[\w\._-]+)/join/$', 'plus_groups.views.join', name='join_group'),
                       url(r'^(?P<resource_id>[\w\._-]+)/apply/$', 'plus_groups.views.apply', name='apply_group'),
                       url(r'^(?P<resource_id>[\w\._-]+)/leave/$', 'plus_groups.views.leave', name='leave_group'),
                       url(r'^(?P<resource_id>[\w\._-]+)/invite/$', 'plus_groups.views.invite', name='invite_to_group'),
                       url(r'^(?P<resource_id>[\w\._-]+)/message/$', 'plus_groups.views.message_members', name='message_members'),
                       url(r'^$', 'plus_groups.views.groups', name='groups'),
                       url(r'^tags/(?P<tag_string>[\w\+\. _-]+)/$', 'plus_groups.views.groups', name='groups_tag'),
                       url(r'^(?P<resource_id>[\d]+)/resources/$', 'plus_groups.views.group_resources', name='group_resources'),
                       url(r'^(?P<resource_id>[\d]+)/resources/tag/(?P<tag_string>[\w\+\. _-]+)/$', 'plus_groups.views.group_resources', name='group_resources_tag'),
                       url(r'^group_type_ajax/$', 'plus_groups.views.group_type_ajax', name='group_type_ajax'),
                       )

