from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.plus_permissions.models import GenericReference
from apps.plus_permissions.decorators import ignore_permissions_exception
from apps.plus_lib.redis_lib import redis
from apps.microblogging.models import Following
from datetime import datetime


FEED_TYPES = (
    (0,'status'),
    (1,'xxx'),
    (2,'join'),
    (3,'leave'),
    (4,'comment'),
    (5,'message'),
    (6,'upload'),
    (7,'create_page'),
    (8,'add link'),
)

# feed items are the only data in the table, but reader feeds are cached in redis

 
def feed_for_key(agent) :
    return "feed_personal_key:%s" % agent.get_ref().id

def clip(s) :
    if len(s) > 140 :
        s = s[0:136]+'...'
    return s

def recreate_feed(key, agent) :
    """ Recreates the queue of feed items for agent """
    from apps.plus_permissions.interfaces import secure_wrap
    subscriptions = Following.objects.followed_by(agent)

    ids = set([])
    for sub in subscriptions :
        for item in FeedItem.feed_manager.get_from(sub) :
            secure_item = secure_wrap(item, agent) 
            if secure_item.has_interface('FeedItem.Viewer') :
                ids.add(item.id)

    pipe = redis.pipeline()
    for item_id in ids :
        pipe.lpush(key, item_id)
    pipe.execute()
    return ids

class FeedManager(models.Manager) :
    def get_from(self, source) :
        "Feed items from source"""
        return self.filter(source=source.get_ref()).order_by('-sent')

    def get_for(self, receiver, start_stop = None) :
        """ Feed items for receiver.
        If we already have a redis list for this receiver, then just pull from it,
        otherwise, recreate from db"""

        key = feed_for_key(receiver)
        if redis.exists(key) :
            if not start_stop :
                start,stop=[0,19]
            else :
                start,stop = start_stop
            ids = redis.lrange(key,start,stop)
        else :
            # ok, we're going to recreate the whole feed again
            ids = recreate_feed(key, receiver)

        return self.filter(id__in=ids).order_by('-sent')

    def all_permissioned(self, agent) :

        from apps.plus_permissions.interfaces import secure_wrap
        def test(x):
            sx = secure_wrap(x, agent)
            return sx.has_interface('FeedItem.Viewer')

        cutoff = 50
        # horribly inefficient, restrict to cutoff for all items
        allowed = [x.id for x in self.all().order_by('-sent')[0:cutoff] 
                   if test(x)]
        return self.filter(id__in=allowed).order_by('-sent')

    def get_status(self, source) :
        feed = self.get_from(source).filter(type=0)
        if feed : 
            return feed[0]
        raise FeedItem.DoesNotExist()


    def update_followers(self, source, item) :
        from apps.plus_permissions.interfaces import secure_wrap
        for f in Following.objects.followers_of(source) :
            # test permission
            secure_item = secure_wrap(item,f)
            if secure_item.has_interface('FeedItem.Viewer') :
                key = feed_for_key(f)
                redis.lpush(key,item.id)
        return item

STATUS = 0
#(1,'xxx')
JOIN = 2
LEAVE = 3
COMMENT = 4
MESSAGE = 5
UPLOAD = 6
WIKI_PAGE = 7
ADD_LINK = 8    

class FeedItem(models.Model) :
    short = models.CharField(_('short'), max_length=140) # 140 character summary 
    expanded = models.TextField(_('expanded'),null=True) # expanded text
    external_link = models.URLField(_('external_link'),null=True) # if there's a link to an outside site, this is it
    type = models.IntegerField(_('type'),choices=FEED_TYPES) # what kind of item is this
    target = models.ForeignKey(GenericReference,
                               related_name ='feed_item_for_this',
                               null=True) # what item in the system this feed item refers to 
    source = models.ForeignKey(GenericReference,
                               related_name ='feed_item_this_posted') # what posted this (probably User or TgGroup. (maybe page))
    
    sent = models.DateTimeField(_('sent'), default=datetime.now)

    feed_manager = FeedManager()


    def __repr__(self) :
        return "<FeedItem %s, from %s, '%s'>" % (self.id, self.source.obj, self.short)

    def has_avatar(self) :
        return (self.source.obj.__class__.__name__ in ['User','TgGroup'])

    STATUS = 0
    CREATE_GROUP = 1
    JOIN = 2
    LEAVE = 3
    COMMENT = 4
    MESSAGE = 5
    UPLOAD = 6
    WIKI_PAGE = 7
    ADD_LINK = 8


    @classmethod
    def post_STATUS(cls, sender, short) :
        new_item = sender.create_FeedItem(sender.get_creator(), type=STATUS, source=sender.get_ref(), short=short) 
        FeedManager().update_followers(sender, new_item)

    @classmethod
    def post_CREATE_GROUP(cls, creator, group) :
        creator_item = creator.create_FeedItem(creator.get_creator(), type=1, source=creator.get_ref(),
                                               short = clip('has created a group : %s' % group.get_display_name()),
                                               target = group.get_ref())
        FeedManager().update_followers(creator, creator_item)
        group_item = group.create_FeedItem(group.get_creator(), type=1, source=group.get_ref(),
                                           short=clip('Created by %s' % creator.get_display_name()),
                                           target = creator.get_ref())
        FeedManager().update_followers(group, group_item)

    @classmethod
    @ignore_permissions_exception
    def post_JOIN(cls, joiner, joined) :
        joiner_item = joiner.create_FeedItem(joiner.get_creator(), type=JOIN, source=joiner.get_ref(),
                                             short = clip('has joined the group %s' % joined.get_display_name()),
                                             target = joined.get_ref())

        FeedManager().update_followers(joiner, joiner_item)

        joined_item = joined.create_FeedItem(joined.get_creator(), type=JOIN, source=joined.get_ref(),
                                             short = clip('%s has joined the group' % joiner.get_display_name()),
                                             target = joiner.get_ref())
        FeedManager().update_followers(joined, joined_item)

    @classmethod
    @ignore_permissions_exception
    def post_LEAVE(cls, leaver, left) :
        leaver_item = leaver.create_FeedItem(leaver.get_creator(), type=LEAVE, source=leaver.get_ref(),
                                             short = clip('has left the group %s' % left.get_display_name()),
                                             target = left.get_ref())

        FeedManager().update_followers(leaver, leaver_item)

        left_item = left.create_FeedItem(left.get_creator(), type=LEAVE, source=left.get_ref(),
                                         short =  clip('%s has left the group.' % leaver.get_display_name()),
                                         target = leaver.get_ref())
        FeedManager().update_followers(left, left_item)


    @classmethod
    def post_ADD_LINK(cls, who, target, url) :
        who_item = who.create_FeedItem(who.get_creator(), type=ADD_LINK, source=who.get_ref(),
                                       short = clip("added a link to %s" % 
                                                    target.get_display_name()),
                                       target = target.get_ref(), external_link=url )

        FeedManager().update_followers(who, who_item)

        target_item = target.create_FeedItem(target.get_creator(), type=ADD_LINK, source=target.get_ref(),
                                             short = clip('%s added a link' % who.get_display_name()),
                                             target = target.get_ref(), external_link=url)
        FeedManager().update_followers(target, target_item)

    @classmethod
    def post_UPLOAD(cls, who, upload) :
        who_item = who.create_FeedItem(who.get_creator(), type=UPLOAD, source=who.get_ref(),
                                       short = clip('uploaded a file %s to %s' % (upload.title, upload.in_agent.obj.get_display_name())),
                                       target = upload.get_ref(), expanded=upload.description)
        FeedManager().update_followers(who, who_item)

        group_item = upload.in_agent.obj.create_FeedItem(upload.in_agent.obj.get_creator(), type=UPLOAD,
                                                         source=upload.in_agent.obj.get_ref(), target=upload.get_ref(),
                                                         short = clip('%s uploaded a file %s' % (who.get_display_name(),
                                                                                                 upload.title)),
                                                         expanded=upload.description)
        FeedManager().update_followers(upload.in_agent.obj, group_item)
 
    @classmethod
    def post_WIKI_PAGE(cls, who, page) :
        who_item = who.create_FeedItem(who.get_creator(), type=WIKI_PAGE, source=who.get_ref(),
                                       short = clip('edited a wiki page %s in %s' % (page.title, page.in_agent.obj.get_display_name())),
                                       target = page.get_ref(), expanded=page.content)
        FeedManager().update_followers(who, who_item)

        group_item = page.in_agent.obj.create_FeedItem(page.in_agent.obj.get_creator(), type=WIKI_PAGE, 
                                                       source=page.in_agent.obj.get_ref(), target=page.get_ref(),
                                                       short = clip('%s edited a page %s' % (who.get_display_name(),
                                                                                             page.title)),
                                                       expanded=page.content)
        FeedManager().update_followers(page.in_agent.obj, group_item)
    

class AggregateFeed(models.Model) :
    """ An AggregateFeed object represents the aggregate of feeds for a group.
    Why? Because group's own feed is a thing in itself. (Ie. not just the aggregate 
    it's members.) We can't automatically forward the members to the parent (this isn't what the  
    reader necessarily wants). So it's better to have an explicit placeholder for the aggregate of 
    a group.

    Because this object itself needs a gen_ref (which is how it can be slotted into the same place as 
    any other thing that has a feed) we need to make it permissionable.
    """
    
    target = models.OneToOneField(GenericReference, related_name='aggregate_feed_object') # in practice, always 

