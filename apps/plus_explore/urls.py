# permission based filtering - need to do this efficiently


# real-time indexing ??
# index pdfs / Office docs


# paginate tabs separately
# fulltext search b) - write template
#                    - reindex
# permalink urls from group_names



# Later
# -- Optimisation - Implement an indexing queuing/batching, to avoid solr "merging" churn when there are a lot of writes
# -- Optimisation - Implement select_related type functionality for GenericForeignKey relationships, and in particular GenericReference's obj attribute
# re-write load_all (haystack) to return a sqlQuery object + play nicely with pagination
# search different sites from one index server using "site" attribute of SearchQuerySet 
# -- listing of members / hosts of a group 


from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^$', 'plus_explore.views.index', name='explore'),
                       url(r'^goto_tag/$', 'plus_explore.views.goto_tag', name='goto_tag'),
                       url(r'^tags/(?P<tag_string>[ \w\+\._-]*)/$', 'plus_explore.views.filter', name='explore_filtered'),  
)
