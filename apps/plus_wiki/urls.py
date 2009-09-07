from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^create_wiki/$', 'apps.plus_wiki.views.create_wiki', name='create_wiki'),
                       )

