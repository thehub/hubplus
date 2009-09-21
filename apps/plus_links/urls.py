from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^add_link/$', 'plus_links.views.add_link', name='add_link'),
)

