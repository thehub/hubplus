from django import template
from django.core.urlresolvers import reverse
from django.template import Context
from apps.plus_permissions.api import TemplateSecureWrapper
from apps.plus_lib.utils import hub_name
from apps.plus_groups.models import Location

from apps.plus_tags.models import get_tags
from django.conf import settings

register = template.Library()

def show_group(context, group):
    #group = TemplateSecureWrapper(group)
    no_of_members = group.get_no_members()
    group_app_label = group.group_app_label()
    urlvar = group_app_label + u':group'
    group_url = reverse(urlvar, args=[group.id])
    return {"group": group, "no_of_members":no_of_members, "group_label":group_app_label, "group_url":group_url}
register.inclusion_tag("group_item.html", takes_context=True)(show_group)



def show_resource(context, item):
    if item.in_agent.obj.place.name == settings.VIRTUAL_HUB_NAME :
        group_label = "group"
    else:
        group_label = hub_name().lower()

    if item.__class__.__name__ == 'SecureWrapper' :
        item = item.get_inner()


    if item.__class__.__name__ == "WikiPage":
        url_name = "view_WikiPage"
        url_name = group_label + "s:"+ url_name
        url = reverse(url_name, args=[item.in_agent.obj.id, item.name])
    elif item.__class__.__name__ == "Resource":
        #url_name = context.current_app + ":view_Resource"
        url_name = 'view_Resource'
        url_name = group_label+"s:"+url_name
        url = reverse(url_name, args=[item.in_agent.obj.id, item.name])
        #download_url = item.download_url()

    tags = get_tags(item)
    #item = TemplateSecureWrapper(item)
    return {'resource':item, 'resource_url':url, 'tags':tags}
register.inclusion_tag("resource_item.html", takes_context=True)(show_resource)

