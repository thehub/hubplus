from django.conf.urls.defaults import *

#allow unicode urls
urlpatterns = patterns('',
                       url(r'^create/$', 'apps.plus_wiki.views.create_wiki', name='create_WikiPage'),
                       url(r'^(?P<page_name>[\w\._-]+)/edit/$', 'apps.plus_wiki.views.edit_wiki', name='edit_WikiPage')               
)

