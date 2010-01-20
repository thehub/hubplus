#!/usr/bin/env python
import sys

from os.path import abspath, dirname, join

try:
    import pinax
except ImportError:
    sys.stderr.write("Error: Can't import Pinax. Make sure you have it installed or use pinax-boot.py to properly create a virtual environment.")
    sys.exit(1)

from django.conf import settings
from django.core.management import setup_environ, execute_from_command_line

try:
    import settings as settings_mod # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

# setup the environment before we start accessing things in the settings.
try :
    setup_environ(settings_mod)
except Exception, e:
    import ipdb
    ipdb.set_trace()


def hello(a):
    print `a`


sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

#from trellis_cache.eventloop import EventQueueSingleton
from trellis_cache.reactor_in_thread import TrellisThread
from mext.context import State

#from settings import trellis

#EventQueueSingleton.activate()
# would be nice for testability to be able to do this before starting the reactor, but that would require EventQueue to be a (non-thread local) Singleton which doesn't seem to be possible in 'Contextual' :-(
 
#trellis.startReactor()


if __name__ == "__main__":
    execute_from_command_line()
