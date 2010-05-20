from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse
from django.conf import settings

from apps.plus_feed.models import FeedItem
import apps.plus_feed.models as feed_models

from django.contrib.auth.models import User

from django.utils.feedgenerator import Rss201rev2Feed, Enclosure

from django.utils.html import strip_tags

# rss for one users
def rss_of_user(request, username) :
    user = User.objects.plus_get(request.user, username=username)
 
    feed = Rss201rev2Feed(title=user.get_display_name(),
                          link='http://'+settings.DOMAIN_NAME+reverse('profile_detail',args=(username,)),
                          description=strip_tags(user.get_profile().about) )
    

    for item in FeedItem.feed_manager.get_from(user) :
                kwargs = {
                          'author_name':user.get_display_name(),
                          'author_copyright':item.source.obj.get_author_copyright(),
                          'pubdate':item.sent,
                          }

                if item.type in [FeedItem.JOIN, FeedItem.LEAVE, FeedItem.UPLOAD, FeedItem.WIKI_PAGE] :
                    link = item.target.obj.get_url()

                else : 
                    link = ''

                description = '' # XXX what should we put into description?

                feed.add_item(item.short, link, description, **kwargs)


    feed_string = feed.writeString('utf-8')
    return HttpResponse(feed_string, mimetype="application/xhtml+xml")


    
