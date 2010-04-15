import hashlib
import urllib

from django import template
from django.contrib.auth.models import User
from apps.plus_groups.models import TgGroup
from django.utils.translation import ugettext as _

from avatar import AVATAR_DEFAULT_URL, AVATAR_DEFAULT_GROUP_URL, AVATAR_DEFAULT_HUB_URL, AVATAR_GRAVATAR_BACKUP

register = template.Library()


class TargetFromNameNotFound(Exception) : 
    pass

def get_true_target(target_obj) :
    if isinstance(target_obj,(str,unicode)) :
        try :
            target_obj = User.objects.get(username=target_obj)
        except User.DoesNotExist:
            try :
                # XXX : when sending a string name we try User *then* TgGroup. 
                # Hence a User with the same name as Group will mask it. 
                # Also, if there's no user with a name, but there is a group, we'll end up with the group's avatar
                target_obj = TgGroup.objects.get(group_name=target_obj)
            except TgGroup.DoesNotExist :
                raise TargetFromNameNotFound(target_obj)
    return target_obj.get_ref()


def get_default_avatar_url(target_obj) :
    if target_obj.is_user() :
        return AVATAR_DEFAULT_URL
    if target_obj.is_hub_type() :
        return AVATAR_DEFAULT_HUB_URL
    return AVATAR_DEFAULT_GROUP_URL


def avatar_url(target_obj, size=80, default_url=AVATAR_DEFAULT_URL):

    try :
        target = get_true_target(target_obj)
    except TargetFromNameNotFound, e:
        return default_url

    avatars = target.avatar_set.order_by('-date_uploaded')

    primary = avatars.filter(primary=True)
    if primary.count() > 0:
        avatar = primary[0]
    elif avatars.count() > 0:
        avatar = avatars[0]
    else:
        avatar = None
    if avatar is not None:
        if not avatar.thumbnail_exists(size):
            avatar.create_thumbnail(size)
        return avatar.avatar_url(size)
    else:
        if AVATAR_GRAVATAR_BACKUP:
            return "http://www.gravatar.com/avatar/%s/?%s" % (
                hashlib.md5(user.email).hexdigest(),
                urllib.urlencode({'s': str(size)}),)
        else:
            return get_default_avatar_url(target_obj)
register.simple_tag(avatar_url)


def avatar(target_obj, size=80, type='group'):

    if type in ['hub','region'] :
        default = AVATAR_DEFAULT_HUB_URL
    elif type == 'group' :
        default = AVATAR_DEFAULT_GROUP_URL
    else :
        default = AVATAR_DEFAULT_URL        
    url = avatar_url(target_obj, size, default)

    if url == default :
        alt = _('Avatar Default')
    else :
        alt = target_obj.get_display_name()
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt,
        size, size)
register.simple_tag(avatar)

def render_avatar(avatar, size=80):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        avatar.avatar_url(size), str(avatar), size, size)
register.simple_tag(render_avatar)
