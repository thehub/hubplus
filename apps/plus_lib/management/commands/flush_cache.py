import sys
from django.utils import termcolors
from django.core.management.base import NoArgsCommand

style = termcolors.make_style(fg='green', opts=('bold',))

from apps.plus_lib.redis_lib import redis


class Command(NoArgsCommand):
    help = 'Empties the redis_cache'
    args = '<filename filename ...>'
    requires_model_validation = False

    def handle_noargs(self, **options):
        print "Flushing Redis Cache", redis.dbsize()
        redis.flushdb()
        print "empty", redis.dbsize()


