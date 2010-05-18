
from django import template
from microblogging.models import Tweet, TweetInstance
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.template import defaultfilters

from apps.plus_feed.models import FeedItem

from apps.plus_permissions.api import secure_wrap

register = template.Library()

@register.inclusion_tag('microblogging/listing.html', takes_context=True)
def tweet_listing(context, tweets, prefix_sender, are_mine) :
    request = context.get('request', None)
    sc = {
        'feed_items': tweets,
        'prefix_sender': prefix_sender,
        'are_mine': are_mine
    }
    if request is not None:
        sc['request'] = request
    return sc



@register.inclusion_tag('microblogging/listing.html', takes_context=True)
def sent_tweet_listing(context, user, prefix_sender, are_mine):
    tweets = Tweet.objects.filter(sender_id=user.pk)
    return tweet_listing(context, tweets, prefix_sender, are_mine)

@register.inclusion_tag('microblogging/form.html', takes_context=True)
def microblogging_form(context, sender, starts_hidden=False) :
    sender_class = ContentType.objects.get_for_model(sender)
    user = context['request'].user

    try :
        status = FeedItem.feed_manager.get_status(sender)
        status_since = defaultfilters.timesince(status.sent)
        status_text = status.short
    except FeedItem.DoesNotExist, e :
        status_since = ''
        status_text = ''

    path = context['request'].path
    
    can_update_status = False
    if sender.__class__.__name__ == 'User' :
        secure = secure_wrap(sender.get_profile(), user)
        can_update_status = secure.has_interface('Profile.Editor')
    else :
        try :
            sender.get_inner()
            secure = sender
        except :
            secure = secure_wrap(sender, user)
        can_update_status = secure.has_interface(secure.get_inner().__class__.__name__ + '.Editor') 


    return {
        'sender':sender,
        'path':path,
        'status_text':status_text,
        'status_since':status_since,
        'sender_class':sender_class,
        'starts_hidden':starts_hidden,
        'can_update_status':can_update_status,
        }
