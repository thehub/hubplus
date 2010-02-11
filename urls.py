from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib import admin

from account.openid_consumer import PinaxConsumer

import os.path

from microblogging.feeds import TweetFeedAll, TweetFeedUser, TweetFeedUserWithFriends
tweets_feed_dict = {"feed_dict": {
    'all': TweetFeedAll,
    'only': TweetFeedUser,
    'with_friends': TweetFeedUserWithFriends,
}}

from blog.feeds import BlogFeedAll, BlogFeedUser
blogs_feed_dict = {"feed_dict": {
    'all': BlogFeedAll,
    'only': BlogFeedUser,
}}

from bookmarks.feeds import BookmarkFeed
bookmarks_feed_dict = {"feed_dict": { '': BookmarkFeed }}

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'apps.account.views.home', name="home"),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^bbauth/', include('bbauth.urls')),
    (r'^authsub/', include('authsub.urls')),
    (r'^members/', include('profiles.urls')),
    
    (r'^plus_tags/', include('plus_tags.urls')),

    (r'^groups/', include('plus_groups.urls', namespace=u'groups', app_name=u'plus_groups'), {'type':'group', 'current_app':'groups'}),
    (r'^hubs/', include('plus_groups.urls', namespace=u'hubs', app_name=u'plus_groups'), {'type':'hub', 'current_app':'hubs'}),
    (r'^regions/', include('plus_groups.urls', namespace=u'regions', app_name=u'plus_groups'), {'type':'hub', 'current_app':'regions'}),

    (r'^resources/', include('resources_search.urls')),

    (r'^plus_wiki/', include('plus_wiki.urls')),
    (r'^plus_comments/', include('plus_comments.urls')),
    (r'^explore/', include('plus_explore.urls')),

    (r'^blog/', include('blog.urls')),
    (r'^invitations/', include('friends_app.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^messages/', include('messages.urls')),
 
    (r'^announcements/', include('announcements.urls')),
    (r'^tweets/', include('microblogging.urls')),
    (r'^tribes/', include('tribes.urls')),
    (r'^projects/', include('projects.urls')),
    (r'^comments/', include('threadedcomments.urls')),
    (r'^robots.txt$', include('robots.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^bookmarks/', include('bookmarks.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^photos/', include('photos.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^swaps/', include('swaps.urls')),
    (r'^flag/', include('flag.urls')),
    (r'^locations/', include('locations.urls')),
    (r'^permissions/', include('plus_permissions.urls')),                       
    (r'^feeds/tweets/(.*)/$', 'django.contrib.syndication.views.feed', tweets_feed_dict),
    (r'^feeds/posts/(.*)/$', 'django.contrib.syndication.views.feed', blogs_feed_dict),
    (r'^feeds/bookmarks/(.*)/?$', 'django.contrib.syndication.views.feed', bookmarks_feed_dict),
    (r'^notices/', include('notification.urls')),

    (r'^lib/', include('plus_lib.urls')),
    (r'^links/', include('plus_links.urls')),

    (r'^testing/sliders/$', direct_to_template, {'template' : 'plus_permissions/tester.html'}),
    (r'^testing/sliders/p$', direct_to_template, {'template' : 'plus_permissions/permissions.html'}), # temp

)

## @@@ for now, we'll use friends_app to glue this stuff together

from photos.models import Image

friends_photos_kwargs = {
    "template_name": "photos/friends_photos.html",
    "friends_objects_function": lambda users: Image.objects.filter(member__in=users),
}

from blog.models import Post

friends_blogs_kwargs = {
    "template_name": "blog/friends_posts.html",
    "friends_objects_function": lambda users: Post.objects.filter(author__in=users),
}

from microblogging.models import Tweet

friends_tweets_kwargs = {
    "template_name": "microblogging/friends_tweets.html",
    "friends_objects_function": lambda users: Tweet.objects.filter(sender_id__in=[user.id for user in users], sender_type__name='user'),
}

from bookmarks.models import Bookmark

friends_bookmarks_kwargs = {
    "template_name": "bookmarks/friends_bookmarks.html",
    "friends_objects_function": lambda users: Bookmark.objects.filter(saved_instances__user__in=users),
    "extra_context": {
        "user_bookmarks": lambda request: Bookmark.objects.filter(saved_instances__user=request.user),
    },
}

urlpatterns += patterns('',
    url('^photos/friends_photos/$', 'friends_app.views.friends_objects', kwargs=friends_photos_kwargs, name="friends_photos"),
    url('^blog/friends_blogs/$', 'friends_app.views.friends_objects', kwargs=friends_blogs_kwargs, name="friends_blogs"),
    url('^tweets/friends_tweets/$', 'friends_app.views.friends_objects', kwargs=friends_tweets_kwargs, name="friends_tweets"),
    url('^bookmarks/friends_bookmarks/$', 'friends_app.views.friends_objects', kwargs=friends_bookmarks_kwargs, name="friends_bookmarks"),
)


if settings.PERMISSION_UPLOADS_THROUGH_X_SENDFILE :
    urlpatterns += patterns('',
        (r'^site_media/member_res/tg.+group/(?P<group_id>[\d]+)/(?P<upload_id>[\d]+)/(?P<path>.*)$', 'plus_permissions.permissioned_static.serve_upload')
    )

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'staticfiles.views.serve')
    )


if settings.SYNC_ENABLED:
    import synced.urls
    urlpatterns += synced.urls.urlpatterns
