from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse
from django.conf import settings

from apps.profiles.models import Profile

from apps.plus_feed.models import FeedItem
import apps.plus_feed.models as feed_models

from django.contrib.auth.models import User
from apps.plus_groups.models import TgGroup

from django.utils.feedgenerator import Rss201rev2Feed, Enclosure

from django.utils.html import strip_tags

from apps.plus_permissions.exceptions import PlusPermissionsNoAccessException

# rss for one users
def rss_of_user(request, username) :

    profile = Profile.objects.plus_get(request.user, user__username=username)
    profile.get_display_name() # test permission
    user = profile.user
    feed = Rss201rev2Feed(title=user.get_display_name(),
                          link='http://'+settings.DOMAIN_NAME+reverse('profile_detail',args=(username,)),
                          description=strip_tags(user.get_profile().about) )
    
    return rss_of(feed, user)


def rss_of_group(request, group_id, current_app, type) :

    group = TgGroup.objects.plus_get(request.user, id=group_id)
    feed = Rss201rev2Feed(title=group.get_display_name(),
                          link = group.get_url(),
                          description=strip_tags(group.description))
    return rss_of(feed, group)


def rss_of_everyone(request) :
    feed = Rss201rev2Feed(title='Hub+',
                          link='http://' + settings.DOMAIN_NAME + reverse('home',args=[]),
                          description='Hub+ is the network that gives you access to the people, resources and knowledge you need to inspire and make your idea come to life.')
    return rss_from_item_list(feed, FeedItem.feed_manager.all_permissioned(request.user))

def rss_of(feed, agent) :
    return rss_from_item_list(feed, FeedItem.feed_manager.get_from(agent))

def rss_from_item_list(feed, item_list) :
    for item in item_list :
        try :
                kwargs = {
                          'author_name': item.source.obj.get_display_name(),
                          'author_copyright':item.source.obj.get_author_copyright(),
                          'pubdate':item.sent,
                          }

                if item.type in [FeedItem.JOIN, FeedItem.LEAVE, FeedItem.UPLOAD, FeedItem.WIKI_PAGE] :
                    if item.target :
                        link = item.target.obj.get_url()
                else : 
                    link = item.source.obj.get_url() + '#tabview=updates_feed'

                description = '' # XXX what should we put into description?

                feed.add_item(item.short, link, description, **kwargs)

        except PlusPermissionsNoAccessException, e :
            pass

    feed_string = feed.writeString('utf-8')
    return HttpResponse(feed_string, mimetype="application/xhtml+xml")


    
