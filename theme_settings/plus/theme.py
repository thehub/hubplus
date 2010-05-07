# selected by PROJECT_THEME

from django.utils.translation import ugettext_lazy as _
PROJECT_NAME=_("Hub+")

COPYRIGHT_HOLDER=_('Hub World Ltd')

VIRTUAL_HUB_NAME = 'hubPlus'
VIRTUAL_HUB_DISPLAY_NAME = 'Hub+ Members'

HUB_NAME_PLURAL = 'Hubs'
EXPLORE_NAME = _('Explore')
HUB_APP_NAME = 'hubs:groups'

TOP_LEVEL_TABS = [(_('Home'), 'home', ''), (EXPLORE_NAME, 'explore', 'explore'), (_('Members'), 'profile_list', 'members'),  (_("Groups"), 'groups:groups', 'groups'), (HUB_NAME_PLURAL, HUB_APP_NAME, 'hubs')]


SITE_NAME = _("Hub+")
SITE_NAME_SHORT = _("Hub+")
SITE_NAME_SENTENCE = _("the Hub+ network")


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

GROUP_INVITES_TO_NON_MEMBERS = True

INVITE_EMAIL_TEMPLATE = """
Dear {{first_name}} {{last_name}},

{{sponsor}} has invited you to become a member of Hub+.

Join and enter a worldwide community of social entrepreneurs and organizations concerned with making the world a better place."""

GROUP_INVITE_SUBJECT_TEMPLATE = """Invitation to join {{group_name}}"""

GROUP_INVITE_TEMPLATE = """
Dear {{first_name}} {{last_name}},

{{sponsor}} has invited you to become a member of {{group_name}} on {{site_name}}.

{{special_message}}

Click on the following link to accept this invitation.

"""

CONTACT_GROUP_INVITE_TEMPLATE = """

{{sponsor}} has invited you to become a member of {{group_name}} on {{site_name}}.

{{special_message}} 

Click on the following link to accept this invitation.


"""

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

