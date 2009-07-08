from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^username_autocomplete/$', 'misc.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    url(r'^$', 'profiles.views.profiles', name='profile_list'),
    url(r'^(?P<username>[\w\._-]+)/$', 'profiles.views.profile', name='profile_detail'),
    url(r'^(?P<username>[\w\._-]+)/field/(?P<fieldname>[\w_]+)/(?P<default>[\w_]*)$','profiles.views.profile_field',{"class":"Profile"},name='profile_field'),
    url(r'^(?P<username>[\w\._-]+)/host_info/field/(?P<fieldname>[\w_]+)/$','profiles.views.profile_field',{"class":"HostInfo"},name='host_info_profile_field'),
    url(r'^(?P<username>[\w\._-]+)/add_tag/$','profiles.views.add_tag', name='add generic_tag'),
    url(r'^(?P<username>[\w\._-]+)/delete_tag/$','profiles.views.delete_tag', name='delete generic_tag'),
    url(r'^(?P<username>[\w\._-]+)/autocomplete_tag/(?P<tag_type>[\w_]+)/$','profiles.views.autocomplete_tag', name='autocomplete generic_tag'),
    url(r'^(?P<username>[\w\._-]+)/map_tags/$','profiles.views.map_tags', name='map users and tags')
)
