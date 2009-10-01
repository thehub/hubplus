from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'microblogging.views.personal', name='tweets_you_follow'),
    url(r'^all/$', 'microblogging.views.public', name='all_tweets'),
    url(r'^(\d+)/$', 'microblogging.views.single', name='single_tweet'),

    url(r'^followers/(\w+)/$', 'microblogging.views.followers', name='tweet_followers'),
    url(r'^following/(\w+)/$', 'microblogging.views.following', name='tweet_following'),
    
    url(r'^toggle_follow/([\w\.]+)/$', 'microblogging.views.toggle_follow', name='toggle_follow'),

    url(r'^ajax_form/(?P<target_type>[\w\.\_]+)/(?P<target_id>[\w\.\_]+)/$', 'microblogging.views.ajax_tweet_form', name='ajax_tweet_form'),
    
    url(r'^ajax_post/$', 'microblogging.views.ajax_post', name='ajax_post'),


)
