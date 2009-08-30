from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^add_tag/(?P<target_class>[\w_]+)/(?P<target_id>[\w_]+)/$','plus_tags.views.add_tag', name='add generic_tag'),
    url(r'^delete_tag/$','plus_tags.views.delete_tag', name='delete generic_tag'),
    url(r'^autocomplete_tag/(?P<target_class>[\w_]+)/(?P<target_id>[\w_]+)/(?P<tag_type>[\w_]+)/$','plus_tags.views.autocomplete_tag', name='autocomplete generic_tag'),
    url(r'^map_tags/$','plus_tags.views.map_tags', name='map users and tags')
)







