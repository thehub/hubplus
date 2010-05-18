
import unittest

from apps.plus_feed.models import FeedItem
from django.contrib.auth.models import User

from apps.microblogging.models import Following

phil = User.objects.get(username='phil.jones')
print [x for x in Following.objects.followers_of(phil)]

print [x for x in Following.objects.followed_by(phil)]
