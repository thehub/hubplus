from django import template
from django.core.urlresolvers import reverse
from django.template import Context
from apps.plus_permissions.api import TemplateSecureWrapper
from apps.plus_lib.utils import hub_name


register = template.Library()

def show_group(context, group):
    group = TemplateSecureWrapper(group)
    no_of_members = group.get_no_members()
    if group.place.name == 'HubPlus':
        group_label = "group"
    else:
        group_label = hub_name().lower()
    urlvar = context.current_app + u':group'
    group_url = reverse(urlvar, args=[group.id])
    return {"group": group, "no_of_members":no_of_members, "group_label":group_label, "group_url":group_url}
register.inclusion_tag("group_item.html", takes_context=True)(show_group)



def show_resource(context, item):
    if item.__class__.__name__ == "WikiPage":
        url_name = "view_WikiPage"
        url_name = context.current_app + ":"+ url_name
        url = reverse(url_name, args=[item.in_agent.obj.id, item.name])
    elif item.__class__.__name__ == "Resource":
        url = item.download_url()

    item = TemplateSecureWrapper(item)
    return {'resource':item, 'resource_url':url}
register.inclusion_tag("resource_item.html", takes_context=True)(show_resource)
