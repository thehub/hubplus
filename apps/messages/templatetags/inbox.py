from django.template import Library, Node

class InboxOutput(Node):
    def render(self, context):
        try:
            user = context['user']
            count = user.received_messages.filter(read_at__isnull=True, recipient_deleted_at__isnull=True).count()
        except (KeyError, AttributeError):
            count = ''
        return "%s" % (count)        
        
def do_print_inbox_count(parser, token):
    """
    A templatetag to show the unread-count for a logged in user.
    Prints the number of unread messages in the user's inbox.
    Usage::
        {% load inbox %}
        {% inbox_count %}
     
    """
    return InboxOutput()

register = Library()     
register.tag('inbox_count', do_print_inbox_count)

from apps.plus_permissions.default_agents import get_all_members_group
from django.core.urlresolvers import reverse

class UrlNode(Node):
    def __init__(self, reverse_string, args=None):
        self.reverse_string = reverse_string
        if not args:
            args = []
        self.args = args

    def render(self, context):
        return reverse(self.reverse_string, args=self.args)


def invite_url(parser, token):
    """
    """
    group = token.split_contents()[1]
    try:
        group = int(group)
    except ValueError:
        group = None

    if group==None:
        group = get_all_members_group().id
    return UrlNode("groups:site_invite", args=[group])
    

register.tag('invite_url', invite_url)
