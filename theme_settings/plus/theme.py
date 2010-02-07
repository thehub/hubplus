# selected by PROJECT_THEME

from django.utils.translation import ugettext_lazy as _
PROJECT_NAME=_("Hub+")

COPYRIGHT_HOLDER=_('Hub World Ltd')

VIRTUAL_HUB_NAME = 'HubPlus'
ALL_MEMBERS_NAME = 'HubPlus'
VIRTUAL_MEMBERS_GROUP_NAME = 'virtual_members'
VIRTUAL_MEMBERS_DISPLAY_NAME = 'Hub+ Virtual'

HUB_NAME_PLURAL = 'Hubs'
EXPLORE_NAME = _('Explore')
HUB_APP_NAME = 'hubs:groups'

TOP_LEVEL_TABS = [(_('Home'), 'home', ''), (EXPLORE_NAME, 'explore', 'explore'), (_('Members'), 'profile_list', 'members'),  (_("Groups"), 'groups:groups', 'groups'), (HUB_NAME_PLURAL, HUB_APP_NAME, 'hubs')]


SITE_NAME = _("Hub+")
SITE_NAME_SHORT = _("Hub+")



GROUP_TYPES = (
    (u'interest', u'Interest'),
    (u'organisation', u'Organisation'),
    (u'project', u'Project'),
    (u'internal', u'Internal'),
    (u'hub', u'Hub'),
)

GROUP_HUB_TYPE = "hub"

HUB_NAME = 'Hub'
MAIN_HUB_NAME = _('Home Hub')


EXPLORE_SEARCH_TITLE = _('explore search title')
MEMBER_SEARCH_TITLE = _('Search Members')
GROUP_SEARCH_TITLE = _('Search Groups')
HUB_SEARCH_TITLE = _('Search Hubs')
RESOURCE_SEARCH_TITLE = _('Search Resources')


TAG_SEARCH_TITLE = _('tag search title')

SIDE_SEARCH_TITLE = _('side search title')

STATUS_COPY = _('What are you thinking about?')

INVITE_EMAIL_TEMPLATE = """
Dear {{first_name}} {{last_name}},

{{sponsor}} has invited you to become a member of Hub+.

Join and enter a worldwide community of social entrepreneurs and organizations concerned with making the world a better place."""

APPLICATION_MESSAGE = """
You have received an application to: {{group_name}}

Please review applications to this group at {{review_url}}.

from: {{first_name}} {{last_name}}, {{organisation}}

email: {{email_address}}

{% if find_out %}

{{first_name}} {{last_name}} found out about {{group_name}} by:

{{find_out}}

{% endif %}

{{first_name}} {{last_name}} wants to join {{group_name}} because:

{{request}}

"""

ACCEPTED_TO_GROUP = _("""

Dear %(applicant)s,

Your application to join Hub+ has been accepted. Please go to <a href="http://plusdev.the-hub.net/">Hub+</a> to get started.

%(accepted_by)s 

""")



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

HIDDEN_GROUPS = []

GROUP_TYPES = (
    (u'interest', u'Interest'),
    (u'organisation', u'Organisation'),
    (u'project', u'Project'),
    (u'internal', u'Internal'),
    (u'hub', u'Hub'),
)

