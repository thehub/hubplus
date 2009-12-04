# selected by PROJECT_THEME

from django.utils.translation import ugettext_lazy as _
PROJECT_NAME=_("Hub+")

COPYRIGHT_HOLDER=_('Hub World Ltd')

VIRTUAL_HUB_NAME = 'HubPlus'
EXPLORE_NAME = _('Explore')

SITE_NAME = _("Hub+")
SITE_NAME_SHORT = _("Hub+")

GROUP_TYPES = (
    (u'interest', u'Interest'),
    (u'organisation', u'Organisation'),
    (u'project', u'Project'),
    (u'internal', u'Internal'),
    (u'hub', u'Hub'),
)


HUB_NAME = 'Hub'
HUB_NAME_PLURAL = 'Hubs'
MAIN_HUB_NAME = 'Main Hub'

EXPLORE_SEARCH_TITLE = _('explore search title')
MEMBER_SEARCH_TITLE = _('Search Members')
GROUP_SEARCH_TITLE = _('Search Groups')
HUB_SEARCH_TITLE = _('Search Hubs')

TAG_SEARCH_TITLE = _('tag search title')

SIDE_SEARCH_TITLE = _('side search title')

STATUS_COPY = _('What are you thinking about?')

INVITE_EMAIL_TEMPLATE = """
Dear {{first_name}} {{last_name}},

{{sponsor}} has invited you to become a member of Hub+.

Join and enter a worldwide community of social entrepreneurs and organizations concerned with making the world a better place."""


APPLICATION_REJECT_TEMPLATE = """                                                    
Dear {{first_name}} {{last_name}},                                                   

Unfortunately, we can not accept you to become a member of Hub+ at this time.

"""

PASSWORD_RESET_TEMPLATE = """

Dear %(display_name)s,

You have requested to change your password, to reset your password click here: %(link)s .

Your username, in case you've forgotten: %(username)s .

You should log in as soon as possible and change your password.

Thanks for using our site!
"""
