# side bar clouds 

# paginate tabs separately
# -- if results set empty, include tag cloud


# ordering
# fulltext search b) - write template
#                    - reindex


# groups to change urls from ints to group_names
# create a form to validate search term and order and current
# permission based filtering - need to do this efficiently
# index pdfs / Office docs


# Later
# re-write load_all to return a sqlQuery object + play nicely with pagination
# search different sites from one index server using "site" attribute of SearchQuerySet 
# -- listing of members / hosts of a group 
# -- Optimisation - Implement an indexing queuing/batching, to avoid solr "merging" churn when there are a lot of writes
# -- Optimisation - Implement select_related type functionality for GenericForeignKey relationships, and in particular GenericReference's obj attribute

from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^$', 'plus_explore.views.index', name='explore'),
                       url(r'^goto_tag/$', 'plus_explore.views.goto_tag', name='goto_tag'),
                       url(r'^tags/(?P<tag_string>[ \w\+\._-]*)/$', 'plus_explore.views.filter', name='explore_filtered'),  
)
