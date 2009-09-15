from django.conf.urls.defaults import *

#below we allow ANY unicode string for the page name
#it seems to work but what security issues might apply here?
urlpatterns = patterns('',
                       url(r'^(?P<page_name>.+)/edit/$', 'apps.plus_wiki.views.edit_wiki', name='edit_WikiPage'),
                       url(r'^(?P<page_name>.+)/create/$', 'apps.plus_wiki.views.create_wiki_page', name='create_WikiPage'),
                       url(r'^(?P<page_name>.+)/delete_stub/$', 'apps.plus_wiki.views.delete_stub_page', name='deletestub_WikiPage'),
                       url(r'^(?P<page_name>.+)/$', 'apps.plus_wiki.views.view_wiki_page', name='view_WikiPage'),
)

