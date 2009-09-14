from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^add_tag/$', 'plus_tags.views.add_tag', name='add_generic_tag'),
    url(r'^delete_tag/$', 'plus_tags.views.delete_tag', name='delete_generic_tag'),
    url(r'^autocomplete_tag/(?P<tag_type>[\w\._-]+)/$', 'plus_tags.views.autocomplete_tag', name='autocomplete_generic_tag'),
    url(r'^map_tags/$', 'plus_tags.views.map_tags', name='map users and tags'),
)







