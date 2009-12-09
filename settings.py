# -*- coding: utf-8 -*-
# Django settings for complete pinax project.

import os.path
import pinax

from django.utils.translation import ugettext_lazy as _

PROJECT_THEME = 'plus'  
# PROJECT_THEME should be over-ridden in local_settings for an alternative theme, 
# and should correspond to one of the directories in theme_settings etc.

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = 'default'

DEBUG = True
TEMPLATE_DEBUG = False # DEBUG

# tells Pinax to serve media through django.views.static.serve.
SERVE_MEDIA = True # DEBUG

ADMINS = (
     ('phil jones', 'phil.jones@the-hub.net'),
)

MANAGERS = ADMINS


# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

#TIME_FORMAT = ''
DATE_FORMAT = _('D, j M Y')

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "site_media")

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '89^ahj730ydh(%+t2$1k3xm!d51=wo$euj@%**kxcuu5n#03b3'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'dbtemplates.loader.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'apps.django403.middleware.Django403Middleware',
    'django_openid.consumer.SessionConsumer',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'misc.middleware.SortOrderMiddleware',
    'djangodblog.middleware.DBLogMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'hubplus.urls' # should be over-ridden in local_settings

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",

    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "account.context_processors.openid",
    "account.context_processors.account",
    "misc.context_processors.contact_email",
    "misc.context_processors.site_name",
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "misc.context_processors.combined_inbox_count",
    "apps.plus_lib.context_processors.configs"
)

COMBINED_INBOX_COUNT_SOURCES = (
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "notification.context_processors.notification",
)

INSTALLED_APPS = (
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django_evolution',

    # external
    'notification', # must be first
    'django_openid',
    'emailconfirmation',
    'django_extensions',
    'robots',
    'dbtemplates',
    'friends',
    'mailer',
    'messages',
    'announcements',
    'oembed',
    'djangodblog',
    'pagination',
#    'gravatar',
    'threadedcomments',
    'wiki',
    'swaps',
    'timezones',
    'app_plugins',
    'voting',
    'tagging',
    'bookmarks',
    'blog',
    'ajax_validation',
    'photologue',
    'avatar',
    'flag',
    'microblogging',
    'locations',
    'uni_form',
    'reversion',
    # internal (for now)
    'about',
    'plus_lib',
    'plus_permissions',
    'analytics',
    'plus_tags',
    'plus_comments',
    'profiles',
    'plus_groups',
    'plus_links',
    'plus_contacts',
    'plus_wiki',
    'plus_user',
    'plus_resources',
    'staticfiles',
    'account',
    'tribes',
    'projects',
    'misc',
    'photos',
    'tag_app',
    'django.contrib.admin',
    'haystack',
    'django403',
    )

HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr' # override in local_settings


ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/%s/" % o.username,
}

AUTH_PROFILE_MODULE = 'profiles.Profile'
SITE_NAME_SENTENCE = ''   # defaults to site_name in plus_lib/context_processors.py
NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

LOGIN_URL = "/account/login"
LOGIN_REDIRECT_URLNAME = "home"

INTERNAL_IPS = (
    '127.0.0.1',
)

ugettext = lambda s: s
LANGUAGES = (
  ('en', u'English'),
  ('de', u'Deutsch'),
  ('es', u'Español'),
  ('fr', u'Français'),
  ('sv', u'Svenska'),
  ('pt-br', u'Português brasileiro'),
  ('he', u'עברית'),
  ('ar', u'العربية'),
  ('it', u'Italiano'),
)

# URCHIN_ID = "ua-..."

CACHE_BACKEND = "locmem:///?max_entries=3000"
FEEDUTIL_SUMMARY_LEN = 60*7 # 7 hours

AUTHENTICATION_BACKENDS = ('plus_user.models.HubspaceAuthenticationBackend',)
ACCOUNT_OPEN_SIGNUP = False # signups must be accompanied by the appropriate token

MARKUP_CHOICES = (
	('html', 'Plain HMTL'),
	('plain', 'Plain Text'),
)

class NullStream(object):
    def write(*args, **kw):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = { 'cloak_email_addresses': True,
                                     'file_insertion_enabled': False,
                                     'raw_enabled': False,
                                     'warning_stream': NullStream(),
                                     'strip_comments': True,}

# if Django is running behind a proxy, we need to do things like use
# HTTP_X_FORWARDED_FOR instead of REMOTE_ADDR. This setting is used
# to inform apps of this fact
BEHIND_PROXY = False

FORCE_LOWERCASE_TAGS = True

WIKI_REQUIRES_LOGIN = True

# Uncomment this line after signing up for a Yahoo Maps API key at the
# following URL: https://developer.yahoo.com/wsregapp/
# YAHOO_MAPS_API_KEY = ''

# See if we can over-ride the default GRAVATAR
AVATAR_GRAVATAR_BACKUP = False
AVATAR_DEFAULT_URL = "/site_media/images/member.jpg"
AVATAR_DEFAULT_GROUP_URL = "/site_media/images/group.jpg"
AVATAR_DEFAULT_HUB_URL = "/site_media/images/hub.jpg"

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
CONTACT_EMAIL = "world.tech.plus@the-hub.net"
SUPPORT_EMAIL = "world.tech.plus@the-hub.net"
DOMAIN_NAME = "plusdemo.the-hub.net"

SYNC_ENABLED = False
HUBPLUSSVCUID = "hubplus"
HUBPLUSSVCPASS = "SECRET"
SYNCER_HOST = "127.0.0.1"
SYNCER_PORT = 9003

DATABASE_ENGINE = ''    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.  
DATABASE_NAME = ''       # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.



SESSION_COOKIE_DODMAIN = ".XXX.net"
HUBSPACE_COMPATIBLE = True # is this running against a HUBSPACE database?
ROOT_URLCONF = 'XXX.urls'

EMAIL_HOST= 'XXX'
EMAIL_HOST_PASSWORD='XXX_EMAIL_PASSWORD'
EMAIL_HOST_USER=''
EMAIL_PORT='25'
EMAIL_USE_TLS=False

HMAC_KEY = "XXXXXXXXX"

# a local_settings file can over-ride the above
try:
    from local_settings import *
except ImportError:
    print "local failed"
    pass


# use theme_settings for psn / plus distinctions etc.
theme_config= __import__('theme_settings.%s.theme' % PROJECT_THEME, globals(), locals(), PROJECT_THEME)

# load the theme_settings
for setting in dir(theme_config):
    if setting == setting.upper():
        locals()[setting] = getattr(theme_config, setting)


# Now setup patches etc.
try:
    from apps.plus_user.models import patch_user_class
    patch_user_class()
    print "import plus_users succeeded"
except ImportError, e:
    print "plus user failed :: " + `e`


try:
    from apps.plus_groups.models import TgGroup
    print "import TgGroup succeeded"
except ImportError, e:
    print "import TgGroup failed :: " + `e`


try:
    from apps.plus_permissions import patch
except ImportError, e:
    print "importing / setting up permissions system failed :: " + `e`


import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
)

try:
    from utils.static_files import compile, get_version_no
    CSS_FILES = ["site.css", "header.css", "main.css", "serendipity.css", "footer.css", "forms.css", "tabview.css", "overlay.css", "permissions.css", "flickr.css", "list-edit-table.css", "jquery.autocomplete.css", "yui2/editor.css", "yui2/menu.css", "yui2/button.css", "yui2/container.css", "yui2/autocomplete.css", "yui2/slider.css"]

    JS_FILES = ["jquery.min.js", "jq.noconflict.js", "ui.core.js", "effects.core.js", "effects.highlight.js", "jquery.bgiframe.min.js", "jquery.autocomplete.min.js", "tools.overlay-1.0.4.min.js", "json2.js", "yui2/build/yahoo-dom-event/yahoo-dom-event.js", "yui2/build/element/element-min.js", "yui2/build/container/container_core-min.js", "yui2/build/menu/menu-min.js", "yui2/build/button/button-min.js", "yui2/build/editor/editor-min.js", "yui2/build/animation/animation-min.js", "yui2/build/logger/logger-min.js", "yui2/build/dragdrop/dragdrop-min.js", "yui2/build/selector/selector-min.js", "yui2/build/tabview/tabview-min.js", "yui2/build/history/history-min.js", "yui2/build/datasource/datasource-min.js", "yui2/build/connection/connection-min.js", "yui2/build/autocomplete/autocomplete-min.js", "editor.js", "ui.accordion.js", "json2.js", "jquery.confirm.js", "jquery.confirm-1.1.js", "hubcms.js", "tab_hist.js", "hubplus.js", "yui2/build/slider/slider-min.js", "plus_resources/replace_file.js", "plus_permissions/views.js", "pinax_libs/comments.js", "plus_links/plus_links.js", "listings.js", "home.js", "plus_microblogging/plus_microblogging.js", "ready.js"]


    compile(JS_FILES, 'site_media/js', 'hubplus_core.js', minified=True)
    compile(CSS_FILES, 'site_media/css', 'hubplus_core.css')
    JS_VERSION_NO = get_version_no("hubplus_core.js", 'site_media/js')
    CSS_VERSION_NO = get_version_no("hubplus_core.css", 'site_media/css')
    DEVELOPMENT = False
except ImportError, e:
    print `e`



