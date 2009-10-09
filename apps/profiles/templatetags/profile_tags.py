from django import template
from apps.plus_permissions.api import secure_wrap, TemplateSecureWrapper
from apps.plus_lib.utils import main_hub_name

register = template.Library()

def show_profile(request, user):
    homehub = user.homeplace.tggroup_set.filter(level='member')[0]
    profile = TemplateSecureWrapper(secure_wrap(user.get_profile(), request.user, interface_names=['Viewer']))
    return {"user": user, "homehub":homehub, "profile":profile, "main_hub_name":main_hub_name()}
register.inclusion_tag("profile_item.html")(show_profile)

def clear_search_url(request):
    getvars = request.GET.copy()
    if 'search' in getvars:
        del getvars['search']
    if len(getvars.keys()) > 0:
        return "%s?%s" % (request.path, getvars.urlencode())
    else:
        return request.path
register.simple_tag(clear_search_url)


