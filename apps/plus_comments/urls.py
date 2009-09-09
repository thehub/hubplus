from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    ### Comments ###
    url(r'^our_comment/(?P<content_type>\d+)/(?P<content_id>\d+)/(?P<target_id>\d+)/$', views.our_comment, name="plus_comment_form"),

) 
