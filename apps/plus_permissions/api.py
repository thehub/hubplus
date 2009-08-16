
""" This is a high-level interface to the permission system. Can answer questions about permissions without involving 
the user creating a lot of other objects. Also you can ask it to give you some default groups such as 'anon' (the group 
to which anyone is a member)"""

from apps.plus_permissions.interfaces import secure_wrap, TemplateSecureWrapper
from apps.hubspace_compatibility.models import Location

def create_root_location():
    root_location, created = Location.objects.get_or_create(name='HubPlus')
    if created :
        root_location.save()
create_root_location()


anonymous_group = self.get_or_create_group('anonymous', 'World', self.root_location)
all_members_group = self.get_or_create_group('all_members','All Members', self.root_location)
site_hosts = self.get_or_create_group('site_hosts','site_hosts', self.root_location)

def has_access(self, agent, resource, interface) :
    """Does the agent have access to this interface in this resource
    """
        
    # we're always interested in the security_context of this resource
    context = self.get_security_context(resource)
    context_type = ContentType.objects.get_for_model(context)

    # which agents have access?
    allowed_agents = GenericReference.objects.filter(securitytag__interface=interface,
                                                     securitytag__context_content_type=context_type,
                                                     securitytag__context_object_id=context.id)
    # probably should memcache both allowed agents (per .View interface) and agents held per user to allow many queries very quickly. e.g. to only return the search results that you have permission to view
    
    allowed_agents = set([a.obj for a in allowed_agents])
    
    if self.anonyoumous_group in allowed_agents: 
        # in other words, if this resource is matched with anyone, we don't have to test 
        #that user is in the "anyone" group
        return True

    agents_held = agent.get_enclosure_set()
    if allowed_agents.intersection(agents_held):
        return True

    return False


def create_security_tag(security_context, interface, agents=[]) :
    t = SecurityTag(security_context=security_context, interface=interface, agents=agents)
    
