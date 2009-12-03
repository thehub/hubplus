
from django import template
from microblogging.models import Tweet, TweetInstance
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.template import defaultfilters


register = template.Library()

@register.inclusion_tag('microblogging/listing.html', takes_context=True)
def tweet_listing(context, tweets, prefix_sender, are_mine) :

    request = context.get('request', None)
    sc = {
        'tweets': tweets.select_related(depth=1),
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
    tweets = TweetInstance.objects.tweets_from(sender).order_by("-sent")
    if tweets :
        latest_status = tweets[0]
        status_since = defaultfilters.timesince(latest_status.sent)
        status_text = latest_status.text
    else:
        status_since = ''
        status_text = ''

    path = context['request'].path

    return {
        'sender':sender,
        'path':path,
        'status_text':status_text,
        'status_since':status_since,
        'sender_class':sender_class,
        'starts_hidden':starts_hidden,
        }
