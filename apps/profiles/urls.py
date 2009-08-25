
from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^username_autocomplete/$', 'misc.views.username_autocomplete_friends', name='profile_username_autocomplete'),
    url(r'^patch_in_profiles$', 'profiles.views.patch_in_profiles', name="patch in hubspace profiles"),
    url(r'^$', 'profiles.views.profiles', name='profile_list'),
    url(r'^(?P<username>[\w\._-]+)/$', 'profiles.views.profile', name='profile_detail'),
    url(r'^(?P<username>[\w\._-]+)/field/(?P<classname>[\w_]+)/(?P<fieldname>[\w_]+)/(?P<default>[\w_]*)$','profiles.views.profile_field',{},name='profile_field'),

    url(r'^(?P<username>[\w\._-]+)/get_main_permission_sliders/','profiles.views.get_main_permission_sliders',name='[profile_get_main_permission_sliders'),
    url(r'^(?P<username>[\w\._-]+)/update_main_permission_sliders/','profiles.views.update_main_permission_sliders',name='[profile_get_main_permission_sliders'),


)
