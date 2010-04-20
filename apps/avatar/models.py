import datetime
import os.path

from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _

from apps.plus_permissions.models import GenericReference

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
try:
    from PIL import Image
except ImportError:
    import Image

from avatar import AVATAR_STORAGE_DIR, AVATAR_RESIZE_METHOD

def avatar_file_path(instance=None, target=None, filename=''):
    if target :
        name= target_name(target)
    else :
        name = instance.target_name()
    return os.path.join(AVATAR_STORAGE_DIR, name, filename)

def target_name(target) :
    if target.__class__.__name__ == 'GenericReference' :
        target = target.obj
    if target.__class__.__name__ == 'User' :
        return '%s'% target.username
    elif target.__class__.__name__ == 'TgGroup' :
        return '%s'% target.group_name
    else :
        raise Exception("An avatar is attached to something (%s,%s), but can't get a name for it."%(target.__class__.__name__,target.id))


class AvatarManager(models.Manager) :
    def get_for_target(self, target_obj, size=80):
        target = target_obj.get_ref()
        avatars = target.avatar_set.order_by('-date_uploaded')
        primary = avatars.filter(primary=True)

        if primary.count() > 0:
            avatar = primary[0]
        elif avatars.count() > 0:
            avatar = avatars[0]
        else:
            raise Avatar.DoesNotExist
        if not avatar.thumbnail_exists(size):
            avatar.create_thumbnail(size)
        return avatar
        

class Avatar(models.Model):

    # XXX we want to get rid of user, but leave it here until we've moved data across
    user = models.ForeignKey(User,null=True) # deprecated, shouldn't be used

    target = models.ForeignKey(GenericReference, null=True)

    primary = models.BooleanField(default=False)
    avatar = models.ImageField(max_length=1024, upload_to=avatar_file_path, blank=True)
    date_uploaded = models.DateTimeField(default=datetime.datetime.now)

    objects = AvatarManager()

    def target_name(self) :
        target = self.target.obj
        return target_name(target)

    def __unicode__(self):
        return _(u'Avatar for %s') % self.target_name()
    
    def save(self, force_insert=False, force_update=False):
        if self.primary:
            avatars = Avatar.objects.filter(target=self.target, primary=True).exclude(id=self.id)
            avatars.update(primary=False)
            self.target.obj.has_avatar = True
            self.target.obj.save()
        super(Avatar, self).save(force_insert, force_update)
    
    def thumbnail_exists(self, size):
        return self.avatar.storage.exists(self.avatar_name(size))
    
    def create_thumbnail(self, size):
        try:
            orig = self.avatar.storage.open(self.avatar.name, 'rb').read()
            image = Image.open(StringIO(orig))
        except IOError:
            return # What should we do here?  Render a "sorry, didn't work" img?
        (w, h) = image.size
        if w != size or h != size:
            if w > h:
                diff = (w - h) / 2
                image = image.crop((diff, 0, w - diff, h))
            else:
                diff = (h - w) / 2
                image = image.crop((0, diff, w, h - diff))
            image = image.resize((size, size), AVATAR_RESIZE_METHOD)
            if image.mode != "RGB":
                image = image.convert("RGB")
            thumb = StringIO()
            image.save(thumb, "JPEG")
            thumb_file = ContentFile(thumb.getvalue())
        else:
            thumb_file = ContentFile(orig)
        thumb = self.avatar.storage.save(self.avatar_name(size), thumb_file)
    
    def avatar_url(self, size):
        return self.avatar.storage.url(self.avatar_name(size))
    
    def avatar_name(self, size):
        return os.path.join(AVATAR_STORAGE_DIR, self.target_name(),
            'resized', str(size), self.avatar.name)

    def full_path(self) :
        return self.avatar.path



