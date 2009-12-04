class StatusDescriptor(object):

    def __get__(self,obj,typ=None):
        from apps.microblogging.models import send_tweet, TweetInstance
        return TweetInstance.objects.tweets_from(obj).order_by("-sent")[0].text

    def __set__(self,obj,val):
        from apps.microblogging.models import send_tweet, TweetInstance
        send_tweet(obj,val)
