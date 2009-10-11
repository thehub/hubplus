# fulltext search
# ordering

# Sunday
# integrate explore_filtered with explore index -- what to do in case of default list vs tag cloud
# make work in context, and without tabs if only one search_type - deploy multiple times? OR abstract parts to respective places

# side bar clouds and searches

from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^$', 'plus_explore.views.index', name='explore'),
                       url(r'^goto_tag/$', 'plus_explore.views.goto_tag', name='goto_tag'),
                       url(r'^(?P<tag_string>[ \w\+\._-]*)/$', 'plus_explore.views.filter', name='explore_filtered'),  
)
