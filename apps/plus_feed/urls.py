from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^one_item/(?P<resource_id>[\d]+)/$', 'plus_feed.views.feed_item', name='feed_item'),

)


