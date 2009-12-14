from django.conf.urls.defaults import *


urlpatterns = patterns('',
                       url(r'^$', 'resources_search.views.resources', name='resources'),
                       url(r'^tags/(?P<tag_string>[\w\+\. _-]+)/$', 'resources_search.views.resources', name='resources_tag'),
)
