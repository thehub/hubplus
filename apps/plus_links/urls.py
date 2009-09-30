from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^add_link/$', 'plus_links.views.add_link', name='add_link'),
    url(r'^remove_link/(?P<resource_id>[\d]+)/$', 'plus_links.views.remove_link', name='remove_link'),
)

